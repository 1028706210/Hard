from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable, Mapping, Sequence
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

import yaml


SNAPSHOT_DATE = "2026-08-23"
RUNOOB_HOST = "www.runoob.com"
LANGUAGES = ("python", "java", "csharp", "cpp")
SOURCE_INDEXES = {
    "python": "https://www.runoob.com/python3/python3-tutorial.html",
    "java": "https://www.runoob.com/java/java-tutorial.html",
    "csharp": "https://www.runoob.com/csharp/csharp-tutorial.html",
    "cpp": "https://www.runoob.com/cplusplus/cpp-tutorial.html",
}
INDEX_GROUPS = {
    SOURCE_INDEXES["python"]: "Python 3 教程",
    SOURCE_INDEXES["java"]: "Java 教程",
    SOURCE_INDEXES["csharp"]: "C# 教程",
    SOURCE_INDEXES["cpp"]: "C++ 教程",
}
MODULE_RULES = {
    "python": (
        ("python-foundations", ("教程", "简介", "环境搭建", "Pycharm", "VScode", "解释器", "虚拟环境", "pip", "有用的资源")),
        ("python-core-types", ("基础语法", "注释", "基本数据类型", "数据类型转换", "运算符", "数字", "字符串")),
        ("python-flow-collections", ("列表", "元组", "字典", "集合", "条件控制", "循环语句", "编程第一步", "推导式", "数据结构", "for 循环", "while 循环")),
        ("python-stdlib-data", ("标准库", "内置函数", "JSON", "XML", "日期和时间", "datetime", "math", "random", "statistics", "operator", "正则", "re 模块", "sys 模块", "Pickle", "StringIO", "queue", "logging", "csv", "hashlib")),
        ("python-functions-iteration", ("迭代器", "生成器", "with", "函数", "lambda", "装饰器", "__name__", "命名空间", "作用域", "类型注解")),
        ("python-modules-io-oop", ("模块", "输入和输出", "File", " OS", "错误和异常", "面向对象")),
        ("python-concurrency-network", ("网络编程", "SMTP", "urllib", "requests", "subprocess", "多线程", "threading", "asyncio")),
        ("python-database-deployment", ("CGI", "mysql", "MongoDB", "uWSGI")),
        ("python-automation-ui-web", ("pyecharts", "selenium", "爬虫", "Scrapy", "Markdown", "PyQt")),
    ),
    "java": (
        ("java-foundations", ("教程", "简介", "开发环境", "基础语法", "注释", "对象和类", "基本数据类型", "变量类型", "变量命名", "修饰符", "运算符", "循环", "条件", "switch")),
        ("java-core-api", ("Number & Math", "Character", "String", "数组", "日期时间", "正则", "方法", "构造方法", "Scanner")),
        ("java-oop-io", ("Stream", "File", "IO", "异常处理", "继承", "Override", "Overload", "多态", "抽象类", "封装", "接口", "枚举", "package")),
        ("java-collections-generics", ("反射", "数据结构", "集合框架", "ArrayList", "LinkedList", "HashSet", "HashMap", "Iterator", "Object", "NIO", "泛型")),
        ("java-network-concurrency", ("序列化", "网络编程", "发送邮件", "多线程", "文档注释", "Applet")),
        ("java-modern-ecosystem", ("Java 8", "Java 9", "MySQL", "常用类库")),
    ),
    "csharp": (
        ("csharp-foundations", ("教程", "简介", "开发环境", "程序结构", "基本语法", "数据类型", "类型转换", "变量", "变量作用域", "常量", "运算符", "判断", "循环")),
        ("csharp-io-metadata", ("预处理器", "正则", "异常", "文件", "特性", "反射")),
        ("csharp-language-features", ("属性", "索引器", "委托", "事件", "集合", "泛型", "匿名方法")),
        ("csharp-oop", ("封装", "方法", "可空类型", "数组", "字符串", "结构体", "枚举", "类", "继承", "多态", "运算符重载", "接口", "命名空间")),
    ),
    "cpp": (
        ("cpp-stl-containers", ("STL", "导入标准库", "标准库", "<iostream>", "<fstream>", "<sstream>", "<iomanip>", "<array>", "<vector>", "<list>", "<forward_list>", "<deque>", "<stack>", "<queue>", "<priority_queue>", "<set>", "<unordered_set>", "<map>", "<unordered_map>", "<bitset>")),
        ("cpp-algorithms-concurrency", ("<algorithm>", "<iterator>", "<functional>", "<numeric>", "<complex>", "<valarray>", "<cmath>", "<string>", "<regex>", "<ctime>", "<chrono>", "<thread>", "<mutex>", "<condition_variable>", "<future>", "<atomic>")),
        ("cpp-oop", ("类 & 对象", "继承", "重载", "多态", "数据抽象", "数据封装", "接口")),
        ("cpp-advanced", ("文件和流", "异常处理", "动态内存", "命名空间", "模板", "预处理器", "信号处理", "多线程", "Web 编程")),
        ("cpp-foundations", ("教程", "简介", "环境设置", "基本语法", "注释", "数据类型", "变量类型", "变量作用域", "常量", "修饰符", "存储类", "运算符", "循环", "判断")),
        ("cpp-core-memory", ("函数", "数字", "数组", "字符串", "指针", "引用", "日期", "时间", "基本的输入输出", "结构体", "vector 容器", "数据结构")),
    ),
}
CAPSTONE_MODULES = {language: f"{language}-capstone" for language in LANGUAGES}


class SourcePolicyError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True)
class SourceEntry:
    title: str
    url: str
    group: str
    module_id: str
    content_type: str
    snapshot_date: str = SNAPSHOT_DATE

    def as_mapping(self) -> dict[str, str]:
        return {
            "title": self.title,
            "url": self.url,
            "group": self.group,
            "module_id": self.module_id,
            "content_type": self.content_type,
            "snapshot_date": self.snapshot_date,
        }


class _CourseNavigationParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._navigation_depth = 0
        self._heading_tag: str | None = None
        self._heading_text: list[str] = []
        self._anchor_href: str | None = None
        self._anchor_text: list[str] = []
        self.group = ""
        self.links: list[tuple[str, str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if not self._navigation_depth and (
            (tag == "nav" and "data-course-navigation" in attributes)
            or (tag == "div" and attributes.get("id") == "leftcolumn")
        ):
            self._navigation_depth = 1
            return
        if not self._navigation_depth:
            return
        self._navigation_depth += 1
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._heading_tag = tag
            self._heading_text = []
        elif tag == "a" and self._anchor_href is None:
            self._anchor_href = attributes.get("href")
            self._anchor_text = []

    def handle_data(self, data: str) -> None:
        if self._heading_tag is not None:
            self._heading_text.append(data)
        if self._anchor_href is not None:
            self._anchor_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if not self._navigation_depth:
            return
        if tag == self._heading_tag:
            self.group = _clean_text("".join(self._heading_text))
            self._heading_tag = None
            self._heading_text = []
        elif tag == "a" and self._anchor_href is not None:
            title = _clean_text("".join(self._anchor_text))
            if title:
                self.links.append((title, self._anchor_href, self.group))
            self._anchor_href = None
            self._anchor_text = []
        self._navigation_depth -= 1


def _clean_text(value: str) -> str:
    return " ".join(value.split())


def assignment_for_title(language: str, title: str) -> tuple[str, str]:
    if language not in LANGUAGES:
        raise SourcePolicyError("invalid_language", f"不支持的课程语言：{language}")
    normalized_title = title.casefold()
    for module_id, keywords in MODULE_RULES[language]:
        if any(keyword.casefold() in normalized_title for keyword in keywords):
            return module_id, _content_type_for_title(title)
    return CAPSTONE_MODULES[language], _content_type_for_title(title)


def _content_type_for_title(title: str) -> str:
    if "测验" in title:
        return "quiz"
    if "实例" in title:
        return "example"
    if "有用的资源" in title:
        return "resource"
    return "lesson"


def normalize_source_url(index_url: str, href: str) -> str:
    resolved = urlsplit(urljoin(index_url, href))
    if resolved.scheme != "https" or resolved.hostname != RUNOOB_HOST:
        raise SourcePolicyError("cross_domain", f"来源链接超出 {RUNOOB_HOST}：{href}")
    return urlunsplit((resolved.scheme, resolved.netloc, resolved.path, resolved.query, ""))


def snapshot_index(
    index_url: str,
    html: str,
    assignments: Mapping[str, Sequence[tuple[str, str]]],
) -> list[SourceEntry]:
    parser = _CourseNavigationParser()
    parser.feed(html)
    parser.close()
    entries: list[SourceEntry] = []
    seen_urls: set[str] = set()
    for title, href, group in parser.links:
        url = normalize_source_url(index_url, href)
        if url in seen_urls:
            continue
        seen_urls.add(url)
        group = group or INDEX_GROUPS.get(index_url, "")
        if not group:
            raise SourcePolicyError("unclassified", f"来源链接缺少目录分组：{url}")
        module_assignments = assignments.get(url)
        if module_assignments is None:
            raise SourcePolicyError("unclassified", f"来源链接没有模块归属：{url}")
        if not module_assignments:
            raise SourcePolicyError("zero_assignment", f"来源链接没有模块归属：{url}")
        if len(module_assignments) != 1:
            raise SourcePolicyError("multiple_assignment", f"来源链接归属多个模块：{url}")
        module_id, content_type = module_assignments[0]
        if not module_id or not content_type:
            raise SourcePolicyError("zero_assignment", f"来源链接缺少模块或内容类型：{url}")
        entries.append(SourceEntry(title, url, group, module_id, content_type))
    return entries


def snapshot_live_index(language: str, index_url: str, html: str) -> list[SourceEntry]:
    parser = _CourseNavigationParser()
    parser.feed(html)
    parser.close()
    assignments: dict[str, list[tuple[str, str]]] = {}
    for title, href, _ in parser.links:
        url = normalize_source_url(index_url, href)
        assignments[url] = [assignment_for_title(language, title)]
    return snapshot_index(index_url, html, assignments)


def _language_for_module(module_id: str) -> str:
    for language in LANGUAGES:
        if module_id.startswith(f"{language}-"):
            return language
    raise SourcePolicyError("invalid_module", f"模块 ID 未声明课程语言：{module_id}")


def build_coverage_report(entries: Iterable[SourceEntry]) -> dict[str, dict[str, int]]:
    coverage = {language: {"expected": 0, "assigned": 0} for language in LANGUAGES}
    for entry in entries:
        language = _language_for_module(entry.module_id)
        coverage[language]["expected"] += 1
        if entry.module_id and entry.content_type:
            coverage[language]["assigned"] += 1
    for language, counts in coverage.items():
        if counts["expected"] == 0:
            raise SourcePolicyError("empty_language", f"课程目录没有来源条目：{language}")
        if counts["assigned"] != counts["expected"]:
            raise SourcePolicyError("incomplete_coverage", f"课程来源覆盖不完整：{language}")
    return coverage


def write_manifest(entries: Sequence[SourceEntry], manifest_path: Path, coverage_path: Path) -> None:
    coverage = build_coverage_report(entries)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    coverage_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        yaml.safe_dump({"sources": [entry.as_mapping() for entry in entries]}, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    coverage_path.write_text(
        json.dumps({"snapshot_date": SNAPSHOT_DATE, "courses": coverage}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def fetch_text(url: str, timeout: float) -> str:
    request = Request(url, headers={"User-Agent": "Hard-source-snapshot/1.0"})
    with urlopen(request, timeout=timeout) as response:
        normalize_source_url(url, response.geturl())
        return response.read().decode(response.headers.get_content_charset() or "utf-8", errors="replace")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="生成菜鸟教程目录来源清单。")
    parser.add_argument("--manifest", type=Path, default=Path("content/sources.yaml"))
    parser.add_argument("--coverage", type=Path, default=Path("docs/content/source-coverage.json"))
    parser.add_argument("--timeout", type=float, default=20.0)
    arguments = parser.parse_args(argv)
    try:
        entries = [
            entry
            for language, index_url in SOURCE_INDEXES.items()
            for entry in snapshot_live_index(language, index_url, fetch_text(index_url, arguments.timeout))
        ]
        write_manifest(entries, arguments.manifest, arguments.coverage)
    except (OSError, SourcePolicyError) as error:
        print(error, file=sys.stderr)
        return 1
    print(json.dumps({"sources": len(entries), "courses": build_coverage_report(entries)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
