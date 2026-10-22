import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

import pytest
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[3]
TOOL_DIRECTORY = PROJECT_ROOT / "tools" / "content"
if str(TOOL_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(TOOL_DIRECTORY))

import check_originality
import snapshot_sources


INDEX_URL = "https://www.runoob.com/python3/python3-tutorial.html"
TUTORIAL_URL = "https://www.runoob.com/python3/python3-tutorial.html"
SYNTAX_URL = "https://www.runoob.com/python3/python3-basic-syntax.html"
FUNCTION_URL = "https://www.runoob.com/python3/python3-function.html"

ALLOWED_SOURCE_FIELDS = {
    "title",
    "url",
    "group",
    "module_id",
    "content_type",
    "snapshot_date",
}
ALLOWED_MODULE_IDS = {
    "python-foundations",
    "python-core-types",
    "python-flow-collections",
    "python-functions-iteration",
    "python-modules-io-oop",
    "python-stdlib-data",
    "python-concurrency-network",
    "python-database-deployment",
    "python-automation-ui-web",
    "python-capstone",
    "java-foundations",
    "java-core-api",
    "java-collections-generics",
    "java-oop-io",
    "java-network-concurrency",
    "java-modern-ecosystem",
    "java-capstone",
    "csharp-foundations",
    "csharp-oop",
    "csharp-language-features",
    "csharp-io-metadata",
    "csharp-capstone",
    "cpp-foundations",
    "cpp-core-memory",
    "cpp-oop",
    "cpp-stl-containers",
    "cpp-algorithms-concurrency",
    "cpp-advanced",
    "cpp-capstone",
}
EXPECTED_COURSE_COUNTS = {"python": 84, "java": 57, "csharp": 42, "cpp": 99}

COURSE_NAVIGATION = """
<html><body>
  <nav data-course-navigation>
    <h2>Python3 入门</h2>
    <a href="/python3/python3-tutorial.html">Python3 教程</a>
    <a href="/python3/python3-tutorial.html">Python3 教程</a>
    <h2>Python3 语法</h2>
    <a href="/python3/python3-basic-syntax.html">Python3 基础语法</a>
    <h2>Python3 函数</h2>
    <a href="/python3/python3-function.html">Python3 函数</a>
  </nav>
  <article><a href="/python3/python3-ignored.html">正文链接不得采集</a></article>
</body></html>
"""

ASSIGNMENTS = {
    TUTORIAL_URL: [("python-foundations", "lesson")],
    SYNTAX_URL: [("python-core-types", "lesson")],
    FUNCTION_URL: [("python-functions-iteration", "lesson")],
}


def test_snapshots_course_navigation_in_order_with_stable_deduplication() -> None:
    entries = snapshot_sources.snapshot_index(INDEX_URL, COURSE_NAVIGATION, ASSIGNMENTS)

    assert [entry.as_mapping() for entry in entries] == [
        {
            "title": "Python3 教程",
            "url": TUTORIAL_URL,
            "group": "Python3 入门",
            "module_id": "python-foundations",
            "content_type": "lesson",
            "snapshot_date": "2026-08-23",
        },
        {
            "title": "Python3 基础语法",
            "url": SYNTAX_URL,
            "group": "Python3 语法",
            "module_id": "python-core-types",
            "content_type": "lesson",
            "snapshot_date": "2026-08-23",
        },
        {
            "title": "Python3 函数",
            "url": FUNCTION_URL,
            "group": "Python3 函数",
            "module_id": "python-functions-iteration",
            "content_type": "lesson",
            "snapshot_date": "2026-08-23",
        },
    ]


def test_snapshots_legacy_left_column_course_navigation() -> None:
    html = """
    <div id="leftcolumn">
      <h2>Python3 入门</h2>
      <a href="/python3/python3-tutorial.html">Python3 教程</a>
    </div>
    """

    entries = snapshot_sources.snapshot_index(INDEX_URL, html, {TUTORIAL_URL: ASSIGNMENTS[TUTORIAL_URL]})

    assert [entry.as_mapping() for entry in entries] == [
        {
            "title": "Python3 教程",
            "url": TUTORIAL_URL,
            "group": "Python3 入门",
            "module_id": "python-foundations",
            "content_type": "lesson",
            "snapshot_date": "2026-08-23",
        }
    ]


def test_uses_the_index_title_for_an_untitled_first_navigation_group() -> None:
    html = """
    <div id="leftcolumn">
      <a href="/python3/python3-tutorial.html">Python3 教程</a>
    </div>
    """

    entries = snapshot_sources.snapshot_index(INDEX_URL, html, {TUTORIAL_URL: ASSIGNMENTS[TUTORIAL_URL]})

    assert entries[0].group == "Python 3 教程"


def test_rejects_cross_domain_navigation_links() -> None:
    html = """
    <nav data-course-navigation>
      <h2>Python3 入门</h2>
      <a href="https://example.test/python">外部链接</a>
    </nav>
    """

    with pytest.raises(snapshot_sources.SourcePolicyError, match="cross_domain"):
        snapshot_sources.snapshot_index(INDEX_URL, html, {})


def test_rejects_navigation_links_without_a_module_assignment() -> None:
    with pytest.raises(snapshot_sources.SourcePolicyError, match="unclassified"):
        snapshot_sources.snapshot_index(INDEX_URL, COURSE_NAVIGATION, {TUTORIAL_URL: ASSIGNMENTS[TUTORIAL_URL]})


@pytest.mark.parametrize(
    ("assignments", "error_code"),
    [
        ({TUTORIAL_URL: []}, "zero_assignment"),
        (
            {
                TUTORIAL_URL: [
                    ("python-foundations", "lesson"),
                    ("python-core-types", "lesson"),
                ]
            },
            "multiple_assignment",
        ),
    ],
)
def test_rejects_zero_or_multiple_module_assignments(
    assignments: dict[str, list[tuple[str, str]]], error_code: str
) -> None:
    html = """
    <nav data-course-navigation>
      <h2>Python3 入门</h2>
      <a href="/python3/python3-tutorial.html">Python3 教程</a>
    </nav>
    """

    with pytest.raises(snapshot_sources.SourcePolicyError, match=error_code):
        snapshot_sources.snapshot_index(INDEX_URL, html, assignments)


def test_coverage_report_requires_every_course_to_have_assigned_sources() -> None:
    entries = [
        snapshot_sources.SourceEntry("Python", TUTORIAL_URL, "Python", "python-foundations", "lesson"),
        snapshot_sources.SourceEntry("Java", "https://www.runoob.com/java/java-tutorial.html", "Java", "java-foundations", "lesson"),
        snapshot_sources.SourceEntry("C#", "https://www.runoob.com/csharp/csharp-tutorial.html", "C#", "csharp-foundations", "lesson"),
        snapshot_sources.SourceEntry("C++", "https://www.runoob.com/cplusplus/cpp-tutorial.html", "C++", "cpp-foundations", "lesson"),
    ]

    report = snapshot_sources.build_coverage_report(entries)

    assert report == {
        "python": {"expected": 1, "assigned": 1},
        "java": {"expected": 1, "assigned": 1},
        "csharp": {"expected": 1, "assigned": 1},
        "cpp": {"expected": 1, "assigned": 1},
    }


def test_coverage_report_rejects_an_empty_course() -> None:
    entry = snapshot_sources.SourceEntry("Python", TUTORIAL_URL, "Python", "python-foundations", "lesson")

    with pytest.raises(snapshot_sources.SourcePolicyError, match="empty_language"):
        snapshot_sources.build_coverage_report([entry])


@pytest.mark.parametrize(
    ("language", "title", "expected"),
    [
        ("python", "Python3 基础语法", ("python-core-types", "lesson")),
        ("java", "Java 集合框架", ("java-collections-generics", "lesson")),
        ("csharp", "C# 文件的输入与输出", ("csharp-io-metadata", "lesson")),
        ("cpp", "C++ <vector>", ("cpp-stl-containers", "lesson")),
        ("python", "Python 量化", ("python-capstone", "lesson")),
        ("java", "Java 测验", ("java-capstone", "quiz")),
        ("python", "Python3 内置函数", ("python-stdlib-data", "lesson")),
        ("csharp", "C# 匿名方法", ("csharp-language-features", "lesson")),
        ("cpp", "C++ STL 教程", ("cpp-stl-containers", "lesson")),
        ("cpp", "C++ 重载运算符和重载函数", ("cpp-oop", "lesson")),
    ],
)
def test_assigns_each_directory_entry_to_one_declared_module(
    language: str, title: str, expected: tuple[str, str]
) -> None:
    assert snapshot_sources.assignment_for_title(language, title) == expected


def test_csharp_foundations_declares_all_thirteen_task42_source_topics() -> None:
    topics = dict(snapshot_sources.MODULE_RULES["csharp"])["csharp-foundations"]

    assert len(topics) == 13
    assert "变量作用域" in topics


def test_snapshots_a_live_index_with_task_module_assignments() -> None:
    entries = snapshot_sources.snapshot_live_index("python", INDEX_URL, COURSE_NAVIGATION)

    assert [(entry.module_id, entry.content_type) for entry in entries] == [
        ("python-foundations", "lesson"),
        ("python-core-types", "lesson"),
        ("python-functions-iteration", "lesson"),
    ]


def test_originality_check_reports_only_irreversible_match_metadata() -> None:
    shared = "甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午"
    lesson = f"Lesson {shared}.\n\n```python\nprint('{shared}')\n```"
    source_html = f"<p>{shared}</p><pre><code>print('{shared}')</code></pre>"

    matches = check_originality.find_long_chinese_matches(lesson, source_html)
    serialized_matches = json.dumps(matches, ensure_ascii=False)

    assert matches == [
        {
            "position": lesson.index(shared),
            "length": len(shared),
            "digest": hashlib.sha256(shared.encode("utf-8")).hexdigest(),
        }
    ]
    assert shared not in str(matches)
    assert shared not in serialized_matches


@pytest.mark.parametrize(
    "lesson",
    [
        "```python\n甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午\n```",
        "正文中的 `甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午` 是内联代码。",
        "    甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午",
        "\t甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午",
    ],
)
def test_originality_check_ignores_all_markdown_code_regions(lesson: str) -> None:
    shared = "甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午"

    assert check_originality.find_long_chinese_matches(lesson, f"<p>{shared}</p>") == []


def test_originality_scan_reads_source_text_temporarily_without_writing_it(tmp_path: Path) -> None:
    shared = "甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午"
    module_directory = tmp_path / "python" / "python-foundations"
    module_directory.mkdir(parents=True)
    lesson_path = module_directory / "intro.md"
    lesson_path.write_text(
        f"""---
source_url: https://www.runoob.com/python3/python3-intro.html
---

{shared}
""",
        encoding="utf-8",
    )
    fetched_urls: list[str] = []

    report = check_originality.scan_module(
        tmp_path,
        "python",
        "python-foundations",
        lambda url: fetched_urls.append(url) or f"<p>{shared}</p>",
    )

    assert fetched_urls == ["https://www.runoob.com/python3/python3-intro.html"]
    assert report == {
        "python/python-foundations/intro.md": [
            {
                "position": lesson_path.read_text(encoding="utf-8").index(shared),
                "length": len(shared),
                "digest": hashlib.sha256(shared.encode("utf-8")).hexdigest(),
            }
        ]
    }
    assert shared not in str(report)
    assert shared not in json.dumps(report, ensure_ascii=False)
    assert list(module_directory.iterdir()) == [lesson_path]


def test_originality_cli_never_emits_matching_source_text(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    shared = "甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午"
    module_directory = tmp_path / "python" / "python-foundations"
    module_directory.mkdir(parents=True)
    (module_directory / "intro.md").write_text(
        f"---\nsource_url: https://www.runoob.com/python3/python3-intro.html\n---\n\n{shared}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(check_originality, "fetch_source_text", lambda _url, _timeout: f"<p>{shared}</p>")

    exit_code = check_originality.main(
        ["--content-root", str(tmp_path), "--language", "python", "--module", "python-foundations"]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 1
    assert shared not in captured.out
    assert shared not in captured.err
    assert shared not in json.dumps(payload, ensure_ascii=False)
    assert payload["matches"]["python/python-foundations/intro.md"][0]["length"] == len(shared)


def test_originality_fetch_retries_transient_failures_without_persisting_source_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[int] = []

    class Response:
        headers = type("Headers", (), {"get_content_charset": lambda _self: "utf-8"})()

        def geturl(self) -> str:
            return "https://www.runoob.com/python3/python3-intro.html"

        def read(self) -> bytes:
            return b"<p>temporary source</p>"

        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *_args: object) -> None:
            return None

    def flaky_urlopen(*_args: object, **_kwargs: object) -> Response:
        calls.append(1)
        if len(calls) < 3:
            raise OSError("temporary network failure")
        return Response()

    monkeypatch.setattr(check_originality, "urlopen", flaky_urlopen)
    monkeypatch.setattr(check_originality, "sleep", lambda _seconds: None)

    assert check_originality.fetch_source_text(
        "https://www.runoob.com/python3/python3-intro.html", 1, retries=2
    ) == "<p>temporary source</p>"
    assert len(calls) == 3


def test_originality_fetch_reports_exhausted_transient_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(check_originality, "urlopen", lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("offline")))
    monkeypatch.setattr(check_originality, "sleep", lambda _seconds: None)

    with pytest.raises(OSError, match="offline"):
        check_originality.fetch_source_text(
            "https://www.runoob.com/python3/python3-intro.html", 1, retries=1
        )


def test_committed_source_manifest_matches_coverage_baseline() -> None:
    manifest = yaml.safe_load((PROJECT_ROOT / "content" / "sources.yaml").read_text(encoding="utf-8"))
    coverage = json.loads((PROJECT_ROOT / "docs" / "content" / "source-coverage.json").read_text(encoding="utf-8"))
    sources = manifest["sources"]

    assert isinstance(sources, list)
    assert len(sources) == sum(EXPECTED_COURSE_COUNTS.values())
    assert all(set(source) == ALLOWED_SOURCE_FIELDS for source in sources)
    assert all(all(isinstance(source[field], str) and source[field] for field in ALLOWED_SOURCE_FIELDS) for source in sources)
    assert all(source["snapshot_date"] == "2026-08-23" for source in sources)
    assert all(
        (parsed := urlsplit(source["url"])).scheme == "https" and parsed.netloc == "www.runoob.com"
        for source in sources
    )
    assert len([source["url"] for source in sources]) == len({source["url"] for source in sources})
    assert {source["module_id"] for source in sources} <= ALLOWED_MODULE_IDS
    assert {source["content_type"] for source in sources} <= {"lesson", "example", "quiz", "resource"}

    assigned = Counter(source["module_id"].split("-", 1)[0] for source in sources)
    assert dict(assigned) == EXPECTED_COURSE_COUNTS
    recomputed_coverage = {
        "snapshot_date": "2026-08-23",
        "courses": {
            language: {"expected": count, "assigned": assigned[language]}
            for language, count in EXPECTED_COURSE_COUNTS.items()
        },
    }
    assert coverage == recomputed_coverage
