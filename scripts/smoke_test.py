#!/usr/bin/env python3
"""Replay a committed issue in a new ignored directory, without publishing anything."""
import argparse
import hashlib
import io
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
COMMON = ('stack_anatomy.json', 'art_plan.md', 'art_layout.json', 'image_prompt.txt',
          'art_base.png', 'art_eval.json', 'post_image.png', 'post_image.png.meta.json')
TARGET = ('final_post.md', 'post_check.json', 'score_report.json')


def destination(root, value):
    root = root.resolve()
    path = (root / value).resolve()
    local = root / '.local'
    if local.is_symlink() or not path.is_relative_to(local) or path == local:
        raise ValueError('Smoke destination must be inside the repository .local directory')
    if path.exists():
        raise ValueError('Smoke destination already exists; choose a new directory')
    return path


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def replay(ref, work, verify_image=False):
    commit = git('rev-parse', '--verify', '--end-of-options', ref + '^{commit}').decode().strip()
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('Expected a full Git commit SHA')
    before = git('status', '--porcelain')
    dossier = git('show', commit + ':out/stack_anatomy.json')
    names = COMMON + (() if json.loads(dossier).get('no_target_this_cycle') else TARGET)
    # Read the complete allowlist first so missing artifacts cannot leave a partial fixture.
    files = {name: git('show', commit + ':out/' + name) for name in names}
    out = work / 'out'
    out.mkdir(parents=True)
    for name, content in files.items():
        (out / name).write_bytes(content)
    result = subprocess.run([sys.executable, 'scripts/run_checks.py', '--out-dir', str(out),
                             '--log-dir', str(work / 'logs')], cwd=ROOT,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    (work / 'checks.log').write_text(result.stdout)
    report = {'artifact_commit': commit, 'artifact_count': len(files),
              'checks_passed': result.returncode == 0, 'logs': str(work / 'logs'),
              'image_verified': False, 'image_verification_requested': verify_image}
    summary_path = work / 'logs/summary.json'
    if summary_path.is_file():
        summary = json.loads(summary_path.read_text())
        report['checks'] = [{'check': row['check'], 'passed': row['passed']}
                           for row in summary['checks']]
    test_log = work / 'logs/tests.log'
    if test_log.is_file():
        count = re.search(r'^Ran (\d+) tests? in ', test_log.read_text(), re.M)
        report['unit_test_count'] = int(count[1]) if count else None
    if verify_image:
        url = ('https://raw.githubusercontent.com/Talonsturgill/linkedin-texas-ai-stack/'
               + commit + '/out/post_image.png')
        with urllib.request.urlopen(url, timeout=30) as response:
            image_bytes = response.read()
            report['image_status'] = response.status
            report['image_content_type'] = response.headers.get_content_type()
        with Image.open(io.BytesIO(image_bytes)) as image:
            report['image_verified'] = (report['image_status'] == 200
                and report['image_content_type'] == 'image/png' and image.format == 'PNG'
                and image.size == (1080, 1080) and image_bytes == files['post_image.png'])
        report['image_url'] = url
        report['image_sha256'] = hashlib.sha256(image_bytes).hexdigest()
    report['tracked_state_preserved'] = before == git('status', '--porcelain')
    report['ok'] = (report['checks_passed'] and report['tracked_state_preserved']
                    and (not verify_image or report['image_verified']))
    (work / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact-ref', required=True)
    parser.add_argument('--work-dir', required=True)
    parser.add_argument('--verify-image', action='store_true')
    args = parser.parse_args()
    try:
        work = destination(ROOT, args.work_dir)
        # Enforce Git's actual ignore rules, rather than trusting the directory name.
        subprocess.run(['git', 'check-ignore', '-q', str(work)], cwd=ROOT, check=True)
        report = replay(args.artifact_ref, work, args.verify_image)
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}))
        return 1
    print(json.dumps(report, indent=2))
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
