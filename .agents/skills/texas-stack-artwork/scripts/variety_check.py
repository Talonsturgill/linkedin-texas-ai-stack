#!/usr/bin/env python3
"""Check semantic cooldowns and low-frequency image structure, ignoring decorative grain."""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

from procedural_art import STYLES, PALETTES, MOTIFS, canonical_style, digest


def fingerprint(path):
    with Image.open(path) as opened:
        image=opened.convert('RGB').filter(ImageFilter.GaussianBlur(8))
        gray=np.asarray(image.convert('L').resize((32,32),Image.Resampling.LANCZOS),float)
        hsv=np.asarray(image.resize((64,64)).convert('HSV'),float)/255
    # Low-frequency DCT ignores paper grain and tiny random dots.
    matrix=np.cos(np.pi*(2*np.arange(32)[None,:]+1)*np.arange(8)[:,None]/64)
    values=(matrix@gray@matrix.T).ravel()[1:]
    bits=values>np.median(values)
    code=sum(int(bit)<<i for i,bit in enumerate(bits))
    hist=np.histogramdd(hsv.reshape(-1,3),bins=(12,2,3),range=((0,1),(0,1),(0,1)))[0].ravel()
    hist=hist/hist.sum()
    return {'version':2,'phash':f'{code:016x}','color_histogram':[round(float(x),6) for x in hist]}


def distances(left,right):
    structural=(int(left['phash'],16)^int(right['phash'],16)).bit_count()/63
    a=np.array(left['color_histogram']);b=np.array(right['color_histogram'])
    color=float(np.sqrt(np.sum((np.sqrt(a)-np.sqrt(b))**2))/np.sqrt(2))
    return {'structure_distance':round(structural,4),'color_distance':round(color,4)}


def validate(spec,history,image):
    errors=[];cooldown=history.get('artwork_cooldowns') or {}
    if spec.get('style_family') in (None,'') or spec.get('render_family') not in STYLES:
        errors.append('Unknown drawing family')
    elif spec['style_family']!=STYLES[spec['render_family']][0]:errors.append('Drawing family renamed')
    checks=(('style_family','style_families_last_8'),('hue_family','hue_families_last_4'),
            ('composition','compositions_last_2'))
    for field,key in checks:
        banned=cooldown.get(key,[])
        if field=='style_family':banned=[canonical_style(x) for x in banned]
        if spec.get(field) in banned:errors.append(field+' repeats its cooldown')
    if not spec.get('motifs') or spec['motifs'][0] in cooldown.get('primary_motifs_last_10',[]):
        errors.append('Primary motif repeats its cooldown')
    if spec.get('motifs',[None])[0] not in MOTIFS:errors.append('Unknown primary motif')
    if spec.get('palette')!=PALETTES.get(spec.get('hue_family')):errors.append('Palette and hue label disagree')
    current=fingerprint(image);comparisons=[]
    recent=history.get('recent_artwork',[])[:8]
    for index,prior in enumerate(recent):
        previous=prior.get('visual_fingerprint')
        if previous is None:errors.append('Prior artwork lacks a raster fingerprint: '+prior.get('branch','unknown'));continue
        distance=distances(current,previous)
        comparison={'branch':prior.get('branch'),'base_sha256':prior.get('base_sha256'),**distance}
        if distance['structure_distance']<.18:
            errors.append('Subject structure is too similar to '+prior.get('branch','prior artwork'))
        if index==0:
            axes=(canonical_style(spec['style_family'])!=canonical_style(prior.get('style_family')),
                  spec['hue_family']!=prior.get('hue_family'),spec['composition']!=prior.get('composition'),
                  spec['motifs'][0]!=(prior.get('motifs') or [None])[0])
            comparison['changed_axes']=sum(axes)
            if sum(axes)<4:errors.append('The previous cover must differ on all four semantic axes')
            if distance['color_distance']<.22:errors.append('Actual colors are too close to the previous cover')
        comparisons.append(comparison)
    return {'schema_version':1,'ok':not errors,'errors':errors,'base_sha256':digest(image),
            'spec_values':{k:spec[k] for k in ('render_family','style_family','hue_family','composition','motifs')},
            'visual_fingerprint':current,'comparisons':comparisons,
            'history_snapshot':{k:history.get(k,{} if k=='artwork_cooldowns' else [])
                                for k in ('artwork_cooldowns','recent_artwork')},
            'thresholds':{'structure_distance_min':.18,'previous_color_distance_min':.22,'previous_changed_axes':4},
            'note':'Raster distances reject similar structure; full-size and thumbnail visual review is still required.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--spec',required=True,type=Path);p.add_argument('--history',required=True,type=Path);p.add_argument('--image',required=True,type=Path);p.add_argument('--out',required=True,type=Path)
    a=p.parse_args();report=validate(json.loads(a.spec.read_text()),json.loads(a.history.read_text()),a.image)
    report['spec_sha256']=digest(a.spec)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'ok':report['ok'],'errors':report['errors'],'comparisons':report['comparisons']}))
    raise SystemExit(0 if report['ok'] else 1)


if __name__=='__main__':main()
