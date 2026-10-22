"""Run existing content gates serially; preserve per-command exit evidence."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
import yaml


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.output.resolve() / 'content'
    output.mkdir(parents=True, exist_ok=True)
    records = []
    for language in ('python', 'java', 'csharp', 'cpp'):
        course = yaml.safe_load((root / 'content' / language / 'course.yaml').read_text(encoding='utf-8'))
        modules = course['modules']
        if not modules:
            raise ValueError(f'No modules: {language}')
        for module in modules:
            module_id = module['id']
            for checker, extra in (
                ('report.py', ['--json', str(output / f'{module_id}.json')]),
                ('check_originality.py', []),
            ):
                command = [sys.executable, str(root / 'tools/content' / checker), '--language', language, '--module', module_id, *extra]
                started = datetime.now(timezone.utc).isoformat()
                print(f'{module_id}: {checker}', flush=True)
                with (output / f'{module_id}-{checker}.log').open('wb') as log:
                    result = subprocess.run(command, cwd=root, stdout=log, stderr=subprocess.STDOUT)
                records.append(dict(command=command, started=started, ended=datetime.now(timezone.utc).isoformat(), exit_code=result.returncode))
                (output / 'commands.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
                if result.returncode:
                    return result.returncode
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
