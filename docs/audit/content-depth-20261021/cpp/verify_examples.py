from pathlib import Path
import json
import subprocess
import tempfile
import sys
import threading

ROOT = Path(__file__).resolve().parents[4]
AUDIT = Path(__file__).parent
compiler = Path('D:/DevTools/msys64/ucrt64/bin/g++.exe')
sys.path.insert(0, str(ROOT/'apps/api/src'))
from hard_api.runners.cpp import CppRunner
from hard_api.runners.contracts import Submission, ExecutableTestCase
results = []
with tempfile.TemporaryDirectory(prefix='cpp-depth-', dir=ROOT/'.tool-cache') as temporary:
    for sample in json.loads((AUDIT/'examples.json').read_text(encoding='utf-8')):
        result = CppRunner().run(Submission(language='cpp', files={'main.py':(ROOT/sample['example']).read_text(encoding='utf-8')}, visible_test_cases=(ExecutableTestCase(stdout=sample['expected']),)), Path(temporary), threading.Event())
        results.append({'lesson': sample['lesson'], 'passed': result.status.value == 'succeeded', 'status':result.status.value, 'diagnostics':result.stderr, 'expected':sample['expected'], 'actual':result.stdout})
        print(sample['lesson'], result.status.value, flush=True)
(AUDIT/'example-results.json').write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(f"C++ examples: {sum(item['passed'] for item in results)}/{len(results)} passed")
raise SystemExit(0 if all(item['passed'] for item in results) else 1)
