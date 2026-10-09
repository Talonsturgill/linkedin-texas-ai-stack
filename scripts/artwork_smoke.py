#!/usr/bin/env python3
"""Render three isolated code-art candidates; never assign aesthetic scores or publish."""
import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.agents/skills/texas-stack-artwork/scripts'))
from procedural_art import plans, render, digest
from variety_check import validate
from compose_cover import compose, font_pair
from art_layout import headline_layout
from review_art import contact_sheet
from smoke_test import destination


def generate(fixture, history, work, headline, date):
    dossier=json.loads((fixture/'stack_anatomy.json').read_text())
    candidates=plans(dossier,history)
    layout=headline_layout(headline,font_pair()[0]); reports=[]
    work.mkdir(parents=True)
    for i,spec in enumerate(candidates,1):
        out=work/f'candidate-{i}';out.mkdir()
        for name in ('stack_anatomy.json','final_post.md','score_report.json','post_check.json'):
            if (fixture/name).is_file():shutil.copy2(fixture/name,out/name)
        spec['dossier_sha256']=digest(out/'stack_anatomy.json')
        (out/'art_spec.json').write_text(json.dumps(spec,indent=2)+'\n')
        (out/'art_layout.json').write_text(json.dumps(layout,indent=2)+'\n')
        plan=f"# Pre-production blueprint\n\n{spec['concept']}\n\nMetaphor only. Three concepts considered: "
        plan+='; '.join(s['concept'] for s in candidates)
        plan+=f"\n\nThe primary motif is {spec['motifs'][0]}. Palette {spec['hue_family']}; composition {spec['composition']}. "
        plan+='The dossier supplies each layer and the binary decision. Code must preserve those bindings. '
        plan+='Measured glyph clearance and the rendered alpha mask protect typography. No maps, seals, labels or claimed engineering geometry. '
        plan+='Risks: generic gate depiction, fine lines disappearing at 300 pixels, and visual similarity to recent covers. '
        plan+='Inspect the real pixels, retain rejected passes, and require 8.5 plus minimum seven and no visual blockers.\n'
        (out/'art_plan.md').write_text(plan)
        (out/'image_prompt.txt').write_text(spec['concept']+'. '+spec['metaphor_limit']+'\n')
        receipt=render(spec,layout,out/'art_base.png');receipt['spec_sha256']=digest(out/'art_spec.json')
        (out/'art_render.json').write_text(json.dumps(receipt,indent=2)+'\n')
        variety=validate(spec,history,out/'art_base.png');variety['spec_sha256']=digest(out/'art_spec.json')
        (out/'art_variety.json').write_text(json.dumps(variety,indent=2)+'\n')
        evaluation={k:spec[k] for k in ('schema_version','source','render_family','style_family','hue_family','palette','composition','motifs','seed')}
        evaluation.update({'concepts':[{'name':s['style_family'],'metaphor':s['concept']} for s in candidates],
                           'selected_concept':spec['concept'],'eval_history':[],'eval_final':{},
                           'renderer_sha256':receipt['renderer_sha256'],'spec_sha256':digest(out/'art_spec.json'),
                           'variety_sha256':digest(out/'art_variety.json')})
        (out/'art_eval.json').write_text(json.dumps(evaluation,indent=2)+'\n')
        compose(base_path=out/'art_base.png',headline=headline,category='WATCH' if dossier.get('no_target_this_cycle') else dossier['selected_mechanism']['category_label'],
                date=date,place='TEXAS',prompt_file=out/'image_prompt.txt',plan_file=out/'art_plan.md',
                eval_file=out/'art_eval.json',out_path=out/'post_image.png',subject_box=receipt['subject_box'],layout_path=out/'art_layout.json')
        contact_sheet(out/'art_base.png',out/'post_image.png',out/'review-sheet.png')
        reports.append({'candidate':i,'style':spec['style_family'],'variety_passed':variety['ok'],
                        'variety_errors':variety['errors'],'cover':str(out/'post_image.png'),'review':str(out/'review-sheet.png')})
    (work/'summary.json').write_text(json.dumps({'candidates':reports,'scored':False},indent=2)+'\n')
    return reports


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fixture-dir',required=True,type=Path);p.add_argument('--history',required=True,type=Path);p.add_argument('--work-dir',required=True);p.add_argument('--headline',required=True);p.add_argument('--date',required=True)
    a=p.parse_args();work=destination(ROOT,a.work_dir)
    print(json.dumps({'candidates':generate(a.fixture_dir,json.loads(a.history.read_text()),work,a.headline,a.date),'scored':False},indent=2))


if __name__=='__main__':main()
