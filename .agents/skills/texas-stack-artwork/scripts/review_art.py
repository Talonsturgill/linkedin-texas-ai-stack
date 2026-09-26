#!/usr/bin/env python3
"""Build a compact visual review sheet or record an actual human/model inspection."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
from qa_check import WEIGHTS, sha256


def contact_sheet(base: Path, cover: Path, destination: Path) -> None:
    sheet=Image.new('RGB',(1240,1020),'#191624');draw=ImageDraw.Draw(sheet)
    for source,x,label in ((base,20,'BASE'),(cover,640,'COMPOSED')):
        with Image.open(source) as im:
            sheet.paste(ImageOps.contain(im.convert('RGB'),(580,580)),(x,36))
            sheet.paste(ImageOps.contain(im.convert('RGB'),(300,300)),(x,678))
        draw.text((x,12),label,fill='#ede6d6')
        draw.text((x,650),'300 PX',fill='#ede6d6')
    destination.parent.mkdir(parents=True,exist_ok=True);sheet.save(destination)


def record(eval_path: Path, review_path: Path, base: Path, cover: Path, select: bool, replace_pass: int | None = None) -> dict:
    ledger=json.loads(eval_path.read_text());review=json.loads(review_path.read_text())
    scores=review.get('scores',{})
    if set(scores)!=set(WEIGHTS) or any(type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=10 for v in scores.values()):
        raise ValueError('supply nine finite observed scores from zero to ten')
    notes=review.get('notes',{})
    if set(notes)!=set(WEIGHTS) or any(not isinstance(v,str) or not v.strip() for v in notes.values()):
        raise ValueError('each dimension needs a specific visual observation')
    if set(review.get('inspected_scales',[]))!={'full','300'}:
        raise ValueError('inspect the actual base and cover at full size and 300 pixels first')
    if not isinstance(review.get('blockers'),list) or any(not isinstance(v,str) or not v.strip() for v in review['blockers']):
        raise ValueError('record blockers as a list, including an empty list when none remain')
    history=ledger.setdefault('eval_history',[])
    if replace_pass is None and len(history)>=6:raise ValueError('six ImageGen passes already recorded')
    if replace_pass is not None and not 1<=replace_pass<=len(history):
        raise ValueError('replacement must identify an existing generation')
    base_hash=sha256(base)
    if replace_pass is not None and history[replace_pass-1].get('base_sha256')!=base_hash:
        raise ValueError('a typography re-review must retain the same generated base')
    if replace_pass is None and any(row.get('base_sha256')==base_hash for row in history):
        raise ValueError('this ImageGen base is already recorded; typography repair is not a new generation')
    weighted=round(sum(scores[k]*w for k,w in WEIGHTS.items()),3)
    row=dict(pass_number=replace_pass or len(history)+1,scores=scores,notes=notes,
             inspected_scales=review['inspected_scales'],blockers=review['blockers'],
             base_sha256=base_hash,cover_sha256=sha256(cover),weighted=weighted,
             passed=weighted>=8.5 and min(scores.values())>=7,
             observations=review.get('observations',''),edit_prompt=review.get('edit_prompt',''))
    if select and row['blockers']:raise ValueError('repair visible blockers before selection')
    if replace_pass is None:history.append(row)
    else:
        row['previous_reviews']=history[replace_pass-1].get('previous_reviews',[])+[
            {k:v for k,v in history[replace_pass-1].items() if k!='previous_reviews'}]
        history[replace_pass-1]=row
    ledger['evaluation_protocol']=2
    if select:
        ledger['eval_final']=row
        ledger['selected_base_sha256']=base_hash
    eval_path.write_text(json.dumps(ledger,indent=2)+'\n')
    return {'pass':row['pass_number'],'weighted':weighted,'numeric_floor_passed':row['passed'],
            'blockers':row['blockers'],'selected':select}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base',required=True,type=Path);p.add_argument('--cover',required=True,type=Path)
    p.add_argument('--sheet',type=Path)
    p.add_argument('--eval',type=Path);p.add_argument('--review',type=Path)
    p.add_argument('--select',action='store_true')
    p.add_argument('--replace-pass',type=int,help='Re-review typography on the same generated base')
    a=p.parse_args()
    if a.sheet:contact_sheet(a.base,a.cover,a.sheet);print(json.dumps({'sheet':str(a.sheet)}))
    if a.review:
        if not a.eval:p.error('--review requires --eval')
        print(json.dumps(record(a.eval,a.review,a.base,a.cover,a.select,a.replace_pass)))
    elif not a.sheet:p.error('choose --sheet or --review')

if __name__=='__main__':main()
