from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable, Sequence
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

import yaml


FENCED_CODE = re.compile(
    r"(?ms)^(?: {0,3})(?P<fence>`{3,}|~{3,})[^\n]*\n.*?^(?: {0,3})(?P=fence)[`~]*[ \t]*(?:\n|$)"
)
INLINE_CODE = re.compile(r"`+[^`\n]*`+")
INDENTED_CODE = re.compile(r"(?m)^(?: {4}|\t).*$")
CHINESE_RUN = re.compile(r"[\u4e00-\u9fff]{16,}")


class _VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._ignored_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"code", "pre", "script", "style"}:
            self._ignored_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"code", "pre", "script", "style"} and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth:
            self.parts.append(data)


def _visible_source_text(source_html: str) -> str:
    parser = _VisibleTextParser()
    parser.feed(source_html)
    parser.close()
    return "".join(parser.parts)


def _mask_code_region(match: re.Match[str]) -> str:
    return "".join("\n" if character == "\n" else " " for character in match.group())


def _lesson_text_without_code(lesson_markdown: str) -> str:
    masked = FENCED_CODE.sub(_mask_code_region, lesson_markdown)
    masked = INLINE_CODE.sub(_mask_code_region, masked)
    return INDENTED_CODE.sub(_mask_code_region, masked)


def _longest_common_chinese_run(lesson_run: str, source_run: str) -> tuple[int, str] | None:
    longest = ""
    longest_start = 0
    for start in range(len(lesson_run) - 15):
        seed = lesson_run[start : start + 16]
        source_start = source_run.find(seed)
        if source_start < 0:
            continue
        length = 16
        while (
            start + length < len(lesson_run)
            and source_start + length < len(source_run)
            and lesson_run[start + length] == source_run[source_start + length]
        ):
            length += 1
        candidate = lesson_run[start : start + length]
        if len(candidate) > len(longest):
            longest = candidate
            longest_start = start
    if not longest:
        return None
    return longest_start, longest


def find_long_chinese_matches(lesson_markdown: str, source_html: str) -> list[dict[str, int | str]]:
    lesson_text = _lesson_text_without_code(lesson_markdown)
    source_text = _visible_source_text(source_html)
    source_runs = CHINESE_RUN.findall(source_text)
    matches: list[dict[str, int | str]] = []
    seen_digests: set[str] = set()
    for lesson_run in CHINESE_RUN.finditer(lesson_text):
        candidates = [
            candidate
            for source_run in source_runs
            if (candidate := _longest_common_chinese_run(lesson_run.group(), source_run)) is not None
        ]
        if not candidates:
            continue
        match_start, longest = max(candidates, key=lambda candidate: len(candidate[1]))
        digest = hashlib.sha256(longest.encode("utf-8")).hexdigest()
        if digest not in seen_digests:
            matches.append(
                {
                    "position": lesson_run.start() + match_start,
                    "length": len(longest),
                    "digest": digest,
                }
            )
            seen_digests.add(digest)
    return matches


def _source_url(lesson_markdown: str) -> str:
    parts = lesson_markdown.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError("课时缺少 YAML front matter。")
    metadata = yaml.safe_load(parts[1])
    if not isinstance(metadata, dict) or not isinstance(metadata.get("source_url"), str):
        raise ValueError("课时缺少来源 URL。")
    return metadata["source_url"]


def scan_module(
    content_root: Path,
    language: str,
    module: str,
    fetcher: Callable[[str], str],
) -> dict[str, list[dict[str, int | str]]]:
    module_directory = content_root / language / module
    report: dict[str, list[dict[str, int | str]]] = {}
    for lesson_path in sorted(module_directory.rglob("*.md")):
        lesson_markdown = lesson_path.read_text(encoding="utf-8")
        matches = find_long_chinese_matches(lesson_markdown, fetcher(_source_url(lesson_markdown)))
        if matches:
            report[lesson_path.relative_to(content_root).as_posix()] = matches
    return report


def fetch_source_text(url: str, timeout: float) -> str:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != "www.runoob.com":
        raise ValueError(f"来源 URL 必须位于 https://www.runoob.com：{url}")
    request = Request(url, headers={"User-Agent": "Hard-originality-check/1.0"})
    with urlopen(request, timeout=timeout) as response:
        redirected = urlsplit(response.geturl())
        if redirected.scheme != "https" or redirected.hostname != "www.runoob.com":
            raise ValueError(f"来源 URL 重定向到站外：{response.geturl()}")
        return response.read().decode(response.headers.get_content_charset() or "utf-8", errors="replace")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="检查课程正文与来源页的连续中文重复。")
    parser.add_argument("--content-root", type=Path, default=Path("content"))
    parser.add_argument("--language", required=True)
    parser.add_argument("--module", required=True)
    parser.add_argument("--timeout", type=float, default=20.0)
    arguments = parser.parse_args(argv)
    try:
        report = scan_module(
            arguments.content_root,
            arguments.language,
            arguments.module,
            lambda url: fetch_source_text(url, arguments.timeout),
        )
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(error, file=sys.stderr)
        return 1
    print(json.dumps({"valid": not report, "matches": report}, ensure_ascii=False))
    return int(bool(report))


if __name__ == "__main__":
    raise SystemExit(main())
