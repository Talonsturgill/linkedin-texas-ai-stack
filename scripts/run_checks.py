#!/usr/bin/env python3
"""Run all release checks once, retaining verbose logs locally and printing one verdict."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out-dir',default='out')
    p.add_argument('--log-dir',default='.local/checks')
    a=p.parse_args();out=Path(a.out_dir).resolve();logs=Path(a.log_dir).resolve();logs.mkdir(parents=True,exist_ok=True)
    py=sys.executable
    checks=[('config',[py,'scripts/check_config.py']),('tests',[py,'-m','unittest','discover','-s','tests','-v']),
            ('skill',[py,str(Path.home()/'.codex/skills/.system/skill-creator/scripts/quick_validate.py'),'.agents/skills/texas-stack-artwork']),
            ('run',[py,'scripts/validate_run.py','--out-dir',str(out),'--report',str(logs/'run.json')])]
    dossier=json.loads((out/'stack_anatomy.json').read_text())
    if not dossier.get('no_target_this_cycle'):
        checks.insert(0,('post',[py,'scripts/check_post.py','--post',str(out/'final_post.md'),'--dossier',str(out/'stack_anatomy.json'),'--report',str(out/'post_check.json')]))
    meta=json.loads((out/'post_image.png.meta.json').read_text())
    checks.append(('art',[py,'.agents/skills/texas-stack-artwork/scripts/qa_check.py','--image',str(out/'post_image.png'),'--base',str(out/'art_base.png'),'--prompt',str(out/'image_prompt.txt'),'--plan',str(out/'art_plan.md'),'--eval',str(out/'art_eval.json'),'--date',meta['date'],'--column','THE TEXAS STACK']))
    results=[]
    for name,cmd in checks:
        r=subprocess.run(cmd,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (logs/(name+'.log')).write_text(r.stdout)
        row={'check':name,'passed':r.returncode==0,'log':str(logs/(name+'.log'))}
        if r.returncode:row['failure_tail']=r.stdout[-2400:]
        results.append(row)
    report={'ok':all(r['passed'] for r in results),'checks':results}
    (logs/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    return 0 if report['ok'] else 1

if __name__=='__main__':sys.exit(main())
