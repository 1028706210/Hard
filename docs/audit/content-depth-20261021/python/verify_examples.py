"""Verify this pass's explicit example/output pairs without using the Runner."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import tempfile

import yaml


PROJECT = Path(__file__).resolve().parents[4]
AUDIT = Path(__file__).resolve().parent
before = json.loads((AUDIT / "before.json").read_text(encoding="utf-8"))
changed = []
checks = []
protected = []
for old in before:
    path = PROJECT / old["path"]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if not old["path"].endswith(".md"):
        assert digest == old["sha256"], f"Non-lesson changed: {path}"
        protected.append(old["path"])
    if digest == old["sha256"]:
        continue
    assert path.suffix == ".md", f"Non-lesson changed: {path}"
    _, metadata, body = path.read_text(encoding="utf-8").split("---", 2)
    current = json.loads(json.dumps(yaml.safe_load(metadata), default=str))
    for key, value in old["front_matter"].items():
        if key not in {"concepts", "objectives"}:
            assert current[key] == value, f"Protected metadata changed: {path} {key}"
    changed.append({
        "path": old["path"], "sha256": digest,
        "body_characters_before": old["body_characters"],
        "body_characters_after": len(body),
    })
    # Parse fences first, so prose/earlier examples cannot cross a closing fence.
    fences = list(re.finditer(r"^```([^\n]*)\n(.*?)^```", body, re.M | re.S))
    example_number = 0
    for code_block, output_block in zip(fences, fences[1:]):
        if code_block[1] != "python" or output_block[1] != "text":
            continue
        between = body[code_block.end():output_block.start()]
        if between.strip() != "预期输出：":
            continue
        example_number += 1
        code, expected = code_block[2], output_block[2]
        with tempfile.TemporaryDirectory(prefix="hard-python-depth-") as directory:
            result = subprocess.run(
                [sys.executable, "-I", "-X", "utf8", "-c", code],
                cwd=directory, text=True, encoding="utf-8", capture_output=True,
                timeout=10,
            )
        actual = result.stdout.replace("\r\n", "\n")
        checks.append({
            "lesson": current["id"], "example": example_number,
            "pass": result.returncode == 0 and actual == expected and not result.stderr,
            "expected_stdout": expected, "actual_stdout": actual,
            "stderr": result.stderr, "exit_code": result.returncode,
        })

report = {
    "scope": "isolated explicit lesson examples only; not Runner or E2E",
    "interpreter": sys.version,
    "changed_lessons": changed,
    "protected_nonlesson_files_unchanged": len(protected),
    "required_metadata_unchanged": True,
    "example_checks": checks,
}
(AUDIT / "verification.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
)
print(f"Changed lessons: {len(changed)}; unchanged non-lesson files: {len(protected)}; "
      f"examples: {len(checks)}; passed: {sum(check['pass'] for check in checks)}")
for check in checks:
    if not check["pass"]:
        print(json.dumps(check, ensure_ascii=False))
if not checks or any(not check["pass"] for check in checks):
    raise SystemExit(1)
