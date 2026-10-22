"""Run saved lesson examples sequentially; never modifies curriculum files."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--javac", required=True)
    parser.add_argument("--java", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--manifest", default="examples.json")
    args = parser.parse_args()
    audit_dir = Path(__file__).resolve().parent
    project = audit_dir.parents[3]
    manifest_path = (audit_dir / args.manifest).resolve()
    if not manifest_path.is_relative_to(audit_dir):
        parser.error("manifest must be within this Java audit directory")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    output_dir = args.output_dir.resolve()
    if not output_dir.is_relative_to(audit_dir):
        parser.error("output-dir must be within this Java audit directory")
    output_dir.mkdir(parents=True, exist_ok=False)
    results = []
    for item in manifest["examples"]:
        lesson = project / item["lesson_path"]
        if hashlib.sha256(lesson.read_bytes()).hexdigest() != item["lesson_sha256"]:
            raise RuntimeError(f"Lesson changed after example extraction: {lesson}")
        name = f"{lesson.parent.name}-{lesson.stem}-{item['example_index']}"
        directory = output_dir / name
        directory.mkdir()
        source = directory / "Main.java"
        source.write_text(item["code"], encoding="utf-8")
        result = {"lesson_path": item["lesson_path"], "example_index": item["example_index"],
                  "code_sha256": item["code_sha256"], "status": "fail"}
        compile_result = subprocess.run(
            [args.javac, "-encoding", "UTF-8", "--release", "17", str(source)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
        )
        result["compile_exit_code"] = compile_result.returncode
        result["compile_stdout"] = compile_result.stdout
        result["compile_stderr"] = compile_result.stderr
        if compile_result.returncode == 0:
            run = subprocess.run(
                [args.java, "-cp", str(directory), "Main"], input=item["stdin"],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
            )
            result.update(exit_code=run.returncode, stdout=run.stdout, stderr=run.stderr,
                          expected_stdout=item["stdout"])
            if run.returncode == item["exit_code"] and run.stdout == item["stdout"]:
                result["status"] = "pass"
        results.append(result)
        (output_dir / "results.json").write_text(json.dumps({
            "javac": args.javac, "java": args.java, "results": results,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{result['status'].upper()} {name}", flush=True)
    passed = sum(result["status"] == "pass" for result in results)
    print(f"JAVA_LESSON_EXAMPLES passed={passed} total={len(results)}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
