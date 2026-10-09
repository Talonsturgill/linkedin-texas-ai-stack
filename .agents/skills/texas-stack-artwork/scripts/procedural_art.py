#!/usr/bin/env python3
"""Story-bound procedural illustration, with distinct drawing families and measured bounds."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SIZE = 1080
VERSION = 2
STYLES = {
    'paper_relief': ('cut-paper relief', ['folded_fan', 'diagonal_traverse', 'vertical_cascade']),
    'engraving': ('copperplate engraving', ['frame_window', 'diagonal_traverse', 'horizon_clamp']),
    'isometric': ('isometric metal sculpture', ['ascending_terraces', 'diagonal_traverse', 'off_axis_orbit']),
    'risograph': ('risograph spot-ink print', ['split_field', 'off_axis_orbit', 'radial_iris']),
    'contours': ('contour landscape', ['horizon_clamp', 'vertical_cascade', 'crossing_branches']),
    'glass': ('stained-glass facets', ['fractured_quilt', 'radial_iris', 'folded_fan']),
    'wireframe': ('luminous wire sculpture', ['off_axis_orbit', 'vertical_cascade', 'diagonal_traverse']),
    'weave': ('woven tapestry', ['orthogonal_weave', 'split_field', 'crossing_branches']),
    'cyanotype': ('cyanotype photogram', ['crossing_branches', 'frame_window', 'vertical_cascade']),
    'ribbons': ('kinetic ribbon sculpture', ['diagonal_traverse', 'folded_fan', 'off_axis_orbit']),
    'tiles': ('glazed ceramic tilework', ['orthogonal_weave', 'fractured_quilt', 'ascending_terraces']),
    'charcoal': ('charcoal chiaroscuro', ['horizon_clamp', 'frame_window', 'split_field']),
}
PALETTES = {
    'cobalt_amber': ['#10182A','#07101F','#E8E5DA','#356EF1','#F3AD34'],
    'coral_ink': ['#27132A','#16081D','#F9E9D5','#EE705C','#6FDBD0'],
    'celadon_red': ['#14291F','#071910','#EBE7D0','#93BE99','#EB594D'],
    'saffron_plum': ['#281126','#14091C','#F0E3C9','#E9B84C','#9C6ABB'],
    'petrol_copper': ['#082830','#071419','#DDE7DA','#39A6B0','#DB916A'],
    'ivory_charcoal': ['#D5C9AA','#242224','#F4ECD9','#6C7380','#D86740'],
    'azure_vermilion': ['#122849','#061326','#E5E7E5','#459AD1','#EB513D'],
    'lilac_citrine': ['#211B35','#100A20','#ECE2EF','#AF8FCA','#D6DB48'],
    'moss_magenta': ['#192515','#0B1309','#E5E8C9','#87A655','#DD6396'],
    'glacier_tangerine': ['#10292B','#061718','#E7EEE3','#8ED5D0','#F59453'],
    'ochre_cyan': ['#2C2116','#160F09','#F3E8C7','#BE8C3D','#66C7CD'],
    'rose_midnight': ['#251421','#120A13','#F8DDD8','#D38D9C','#92AEC6'],
}
MOTIFS = ('split key', 'wedge stop', 'iris shutter', 'pivot lever', 'ratchet tooth',
          'sliding pin', 'bridge gap', 'folded clasp', 'perforated sieve', 'forked conduit',
          'counterweight', 'locking collar', 'ribbon knot', 'hinged door', 'lens mask',
          'release buckle')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def story(dossier):
    mechanism = dossier.get('selected_mechanism') or {}
    if dossier.get('no_target_this_cycle'):
        return {'name': 'Incomplete source chain', 'no_target': True, 'layers': [],
                'decision': 'Withhold publication until the evidence chain is complete',
                'controller': 'Editorial verification', 'gate_order': 1}
    layers = mechanism.get('layers') or []
    if not 3 <= len(layers) <= 5:
        raise ValueError('A procedural target needs the verified three-to-five-layer dossier')
    gate = mechanism.get('chokepoint') or {}
    if gate.get('layer_order') not in [row['order'] for row in layers]:
        raise ValueError('The visible gate must bind to a dossier layer')
    return {'name': mechanism['name'], 'no_target': False,
            'layers': [{'order': r['order'], 'name': r['name'], 'controller': r['controlling_actor'],
                        'function': r['function'], 'source_url': r['primary_source']['url']} for r in layers],
            'decision': gate['binary_decision'], 'controller': gate['controlling_actor'],
            'gate_order': gate['layer_order']}


def canonical_style(value):
    value = str(value).lower()
    for key, (label, _) in STYLES.items():
        if value in (key, label): return label
    if 'paper' in value or 'relief' in value: return STYLES['paper_relief'][0]
    if 'clay' in value or 'ceramic' in value or 'plaster' in value: return STYLES['tiles'][0]
    if 'woodcut' in value or 'engrav' in value: return STYLES['engraving'][0]
    if 'cyanotype' in value: return STYLES['cyanotype'][0]
    if 'screenprint' in value or 'risograph' in value: return STYLES['risograph'][0]
    return value


def story_treatment(binding):
    decision = binding['decision'].lower()
    if not binding['no_target'] and 'written' in decision and any(word in decision for word in ('approval', 'permission', 'authorization')):
        return 'written_authorization'
    return 'incomplete_evidence' if binding['no_target'] else 'binary_gate'


def plans(dossier, history, count=3, salt=''):
    binding = story(dossier)
    cooldown = history.get('artwork_cooldowns') or {}
    banned_styles = {canonical_style(x) for x in cooldown.get('style_families_last_8', [])}
    banned_hues = set(cooldown.get('hue_families_last_4', []))
    banned_comp = set(cooldown.get('compositions_last_2', []))
    banned_motifs = set(cooldown.get('primary_motifs_last_10', []))
    seed = int(hashlib.sha256((dossier['run_date'] + binding['name'] + salt).encode()).hexdigest()[:16], 16)
    rng = np.random.default_rng(seed)
    available = [(k, v) for k, v in STYLES.items() if v[0] not in banned_styles]
    rng.shuffle(available)
    hues = [k for k in PALETTES if k not in banned_hues]
    motifs = [k for k in MOTIFS if k not in banned_motifs]
    rng.shuffle(hues); rng.shuffle(motifs)
    result = []
    for key, (label, comps) in available:
        chosen_compositions = {s['composition'] for s in result}
        choices = [c for c in comps if c not in banned_comp and c not in chosen_compositions]
        if not choices or not hues or not motifs: continue
        i = len(result); hue = hues[i % len(hues)]
        result.append({'schema_version': 1, 'generator_version': VERSION, 'source': 'procedural',
                       'render_family': key, 'style_family': label, 'hue_family': hue,
                       'palette': PALETTES[hue], 'composition': str(rng.choice(choices)),
                       'motifs': [motifs[i % len(motifs)]], 'seed': int(rng.integers(1, 2**31)),
                       'story_binding': binding, 'metaphor_limit': 'Editorial metaphor, not an engineering drawing',
                       'story_treatment': story_treatment(binding),
                       'concept': label + ' showing ' + binding['controller'] + ' controlling ' + binding['decision']})
        if len(result) == count: break
    if len(result) < count:
        raise ValueError('Variety catalog exhausted; extend a drawing family instead of relaxing cooldowns')
    return result


class Painter:
    """Draw in normalized subject space at twice output resolution."""
    def __init__(self, spec, zone):
        self.spec = spec; self.zone = zone; self.scale = 2
        self.layer = Image.new('RGBA', (SIZE*2, SIZE*2)); self.draw = ImageDraw.Draw(self.layer)
        self.bg, self.dark, self.light, self.main, self.accent = spec['palette']
        self.rng = np.random.default_rng(spec['seed'])
        self.n = max(3, len(spec['story_binding']['layers']))
        self.gate = spec['story_binding']['gate_order'] - 1
        self.shift = (spec['seed'] % 5 - 2) * .016

    def xy(self, point):
        x,y=point
        comp=self.spec['composition']
        if comp in ('vertical_cascade','crossing_branches'): x,y=y,x
        elif comp in ('off_axis_orbit','folded_fan'): x,y=1-x,y
        elif comp in ('split_field','horizon_clamp'): y=.12+y*.76
        elif comp == 'ascending_terraces': x,y=.10+x*.80,.07+y*.86
        x = .04 + x*.92 + self.shift; y = .06 + y*.88
        l,t,r,b=self.zone
        return (round((l+x*(r-l))*2), round((t+y*(b-t))*2))

    def poly(self, points, fill, stroke=None, width=1):
        ps=[self.xy(p) for p in points]; self.draw.polygon(ps, fill=fill)
        if stroke: self.draw.line(ps+[ps[0]], fill=stroke, width=width*2, joint='curve')

    def line(self, points, fill, width=2):
        self.draw.line([self.xy(p) for p in points], fill=fill, width=width*2, joint='curve')

    def ellipse(self, box, fill, stroke=None, width=1):
        a=self.xy(box[:2]); b=self.xy(box[2:]); coords=(min(a[0],b[0]),min(a[1],b[1]),max(a[0],b[0]),max(a[1],b[1]))
        self.draw.ellipse(coords,fill=fill,outline=stroke,width=width*2)

    def rect(self, box, fill, stroke=None, width=1):
        l,t,r,b=box; self.poly([(l,t),(r,t),(r,b),(l,b)], fill, stroke,width)

    def curve(self, points, fill, width=4):
        # Cubic Bezier, sampled once; crisp supersampling avoids another native dependency.
        if len(points)==4:
            a,b,c,d=np.array(points); ts=np.linspace(0,1,100)
            points=[tuple((1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d) for t in ts]
        self.line(points,fill,width)


def paper(p):
    for i in range(p.n):
        x=.04+i*.19; y=.18+(i%2)*.22
        p.poly([(x+.02,y+.06),(x+.18,y+.08),(x+.17,y+.59),(x+.01,y+.57)],p.dark)
        p.poly([(x,y),(x+.17,y+.03),(x+.17,y+.53),(x,y+.50)],p.accent if i==p.gate else p.main,p.light,1)
        p.poly([(x,y),(x+.08,y+.04),(x+.08,y+.49),(x,y+.50)],p.light)
        p.poly([(x+.08,y+.04),(x+.17,y+.03),(x+.17,y+.53),(x+.08,y+.49)],p.main)
        p.line([(x+.04,y+.20),(x+.17,y+.23)],p.dark,3)
        if i<p.n-1:p.poly([(x+.13,y+.34),(x+.27,y+.22),(x+.28,y+.31),(x+.15,y+.43)],p.accent)
    for j in range(16):p.line([(.03+j*.061,.88),(.055+j*.061,.90)],p.light,1)


def engraving(p):
    p.rect((.02,.05,.97,.95),None,p.light,2)
    p.rect((.035,.075,.955,.925),None,p.main,1)
    for r in np.linspace(.13,.37,10): p.ellipse((.48-r,.5-r,.48+r,.5+r),None,p.light,1)
    for a in np.linspace(0,math.tau,54):
        p.line([(.48+.13*math.cos(a),.5+.13*math.sin(a)),(.48+.35*math.cos(a),.5+.35*math.sin(a))],p.light,1)
    for i in range(p.n):
        x=.08+i*.18; y=.12+(i%2)*.63
        p.rect((x,y,x+.115,y+.13),p.main,p.light,1)
        for j in range(7):p.line([(x,y+j*.02),(x+.115,y+.07+j*.009)],p.light,1)
        p.line([(x+.06,y+.06),(.48,.5)],p.accent if i==p.gate else p.main,4)


def isometric(p):
    for i in reversed(range(p.n)):
        x=.12+i*.145; y=.26+i*.075
        p.poly([(x,y+.1),(x+.25,y-.02),(x+.39,y+.11),(x+.14,y+.24)],p.light,p.dark,2)
        p.poly([(x+.14,y+.24),(x+.39,y+.11),(x+.39,y+.28),(x+.14,y+.41)],p.main,p.dark,2)
        p.poly([(x,y+.1),(x+.14,y+.24),(x+.14,y+.41),(x,y+.27)],p.accent if i==p.gate else p.dark,p.light,1)
        for j in range(8):p.line([(x+.18+j*.026,y+.28-j*.013),(x+.18+j*.026,y+.34-j*.013)],p.light,1)
    p.line([(.13,.84),(.72,.84),(.9,.64)],p.accent,4)


def risograph(p):
    for i in range(p.n):
        x=.16+i*.17; y=.28+(i%2)*.28
        p.ellipse((x-.14,y-.20,x+.14,y+.20),p.accent if i==p.gate else p.main)
        p.ellipse((x-.072,y-.095,x+.072,y+.095),p.bg)
    p.poly([(.06,.76),(.75,.07),(.92,.12),(.24,.84)],p.light)
    p.poly([(.06,.80),(.76,.11),(.84,.14),(.14,.85)],p.accent)
    for y in np.arange(.09,.91,.026):
        for x in np.arange(.07,.94,.021):
            if .13<x+y*.6<.85:p.ellipse((x,y,x+.0035,y+.005),p.dark)


def contours(p):
    for i in range(48):
        ys=.08+i*.017
        pts=[]
        for x in np.linspace(.025,.975,170):
            y=ys+.065*math.sin(x*9+i*.10)+.025*math.sin(x*23+i*.12)
            pts.append((x,y))
        p.line(pts,p.accent if i in (12,13,14) else p.main if i%3 else p.light,2 if i%3 else 3)
    p.poly([(.40,.10),(.55,.08),(.63,.85),(.49,.90)],p.dark,p.accent,3)
    for i in range(p.n):p.line([(.43,.22+i*.135),(.60,.20+i*.135)],p.accent if i==p.gate else p.light,6)


def glass(p):
    center=(.5,.49)
    for i in range(30):
        a=math.tau*i/30;b=math.tau*(i+1)/30
        u=(.5+.48*math.cos(a),.5+.43*math.sin(a));v=(.5+.48*math.cos(b),.5+.43*math.sin(b))
        mid=(.5+.20*math.cos((a+b)/2),.5+.20*math.sin((a+b)/2))
        p.poly([u,v,mid],(p.main,p.accent,p.light)[i%3],p.dark,5)
        p.poly([u,mid,center],p.light if i%3 else p.main,p.dark,5)
    for i in range(p.n):
        a=math.tau*i/p.n
        p.ellipse((.5+.32*math.cos(a)-.022,.5+.28*math.sin(a)-.03,.5+.32*math.cos(a)+.022,.5+.28*math.sin(a)+.03),p.dark,p.light,2)


def wireframe(p):
    for offset in np.linspace(-.1,.1,19):
        pts=[]
        for t in np.linspace(0,math.tau*2,230):
            x=.09+t/(math.tau*2)*.81; y=.5+(.18+offset)*math.sin(t)+offset*.8
            if .44<x<.55:continue
            pts.append((x,y))
        # Separate at the real visual gap instead of bridging it with a sampled chord.
        p.line([v for v in pts if v[0]<.44],p.main,1)
        p.line([v for v in pts if v[0]>.55],p.light,1)
    for i in range(p.n):
        x=.10+i*.20
        p.poly([(x,.19),(x+.055,.14),(x+.055,.80),(x,.85)],None,p.accent if i==p.gate else p.main,2)
    p.line([(.12,.89),(.90,.89)],p.accent,1)


def weave(p):
    for i in range(42):
        x=.035+i*.022
        p.line([(x,.05),(x,.95)],p.main if i%4 else p.accent,9)
    for j in range(24):
        y=.055+j*.038
        for i in range(12):
            x=.025+i*.079
            if (i+j)%2==0:p.line([(x,y),(x+.074,y)],p.light,10)
            else:p.line([(x+.02,y),(x+.065,y)],p.dark,9)
    p.poly([(.43,.05),(.54,.05),(.58,.93),(.46,.93)],p.dark,p.accent,3)
    for i in range(p.n):p.rect((.46,.14+i*.16,.56,.22+i*.16),p.accent if i==p.gate else p.light,p.dark,2)


def cyanotype(p):
    for i in range(p.n):
        x=.10+i*.19
        p.curve([(x,.90),(x+.02,.54),(.5,.62),(.52,.24)],p.light,9)
        for j in range(10):
            t=j/11;y=.88-t*.54
            p.poly([(x,y),(x-.045,y-.045),(x-.018,y-.10),(x+.012,y-.018)],p.light)
            p.line([(x,y),(x-.024,y-.061)],p.main,1)
    for r in np.linspace(.08,.21,7):p.ellipse((.52-r,.27-r,.52+r,.27+r),None,p.light,2)
    p.rect((.38,.17,.65,.22),p.accent)


def ribbons(p):
    for i in reversed(range(p.n)):
        y=.20+i*.135
        pts=[(.04,y),(.36,y-.21),(.60,y+.22),(.95,y-.04)]
        p.curve([(x+.014,z+.025) for x,z in pts],p.dark,34)
        p.curve(pts,p.accent if i==p.gate else p.main,28)
        p.curve([(x,z-.014) for x,z in pts],p.light,3)
        for k in range(7):p.curve([(x,z+k*.005) for x,z in pts],p.light if k==0 else p.main,1)
    p.line([(.47,.09),(.57,.92)],p.dark,24)
    p.line([(.48,.09),(.58,.92)],p.accent,6)


def tiles(p):
    for row in range(3):
        for col in range(5):
            x=.03+col*.19;y=.06+row*.29
            p.rect((x+.007,y+.02,x+.184,y+.27),p.dark)
            p.rect((x,y,x+.17,y+.25),p.main if (row+col)%3 else p.light,p.dark,2)
            p.line([(x+.012,y+.016),(x+.15,y+.016)],p.light,3)
            p.ellipse((x+.043,y+.058,x+.135,y+.20),None,p.dark,12)
            p.ellipse((x+.047,y+.060,x+.131,y+.196),None,p.accent if col==p.gate else p.light,5)
    p.line([(.13,.045),(.88,.045)],p.accent,3)


def charcoal(p):
    for j in range(130):
        y=float(p.rng.uniform(.30,.77));x=float(p.rng.uniform(.03,.35))
        p.curve([(x,y),(.37,y-.2),(.69,y+.16),(.94,y-.06)],p.main, int(p.rng.integers(1,6)))
    for i in range(p.n):
        x=.08+i*.20;y=.12+(i%2)*.12
        p.poly([(x,y),(x+.105,y-.04),(x+.13,.90),(x-.008,.93)],p.dark,p.light,2)
        for j in range(22):p.line([(x+j*.004,y+.03),(x+.013+j*.004,.86)],p.light if j%3==0 else p.main,1)
    p.line([(.04,.18),(.94,.77)],p.accent,9)


RENDERERS = dict(zip(STYLES,(paper,engraving,isometric,risograph,contours,glass,wireframe,weave,cyanotype,ribbons,tiles,charcoal)))


def written_artifact(p):
    """A blank folded sheet through the gate makes a written decision visible without fake text."""
    if story_treatment(p.spec['story_binding']) != 'written_authorization':
        return
    points=[(.36,.24),(.61,.24),(.68,.34),(.68,.78),(.36,.78)]
    p.poly([(x+.014,y+.020) for x,y in points],p.dark)
    p.poly(points,p.light,p.dark,3)
    p.poly([(.61,.24),(.61,.34),(.68,.34)],p.main,p.dark,2)
    # Rules are abstract ink marks, never a copied signature, seal, status or invented wording.
    for y,right in ((.64,.59),(.685,.62),(.73,.55)):
        p.line([(.405,y),(right,y)],p.dark,3)
    family=p.spec['render_family']
    if family=='glass':
        p.poly([(.36,.24),(.48,.24),(.36,.42)],p.main,p.dark,2)
        p.poly([(.68,.60),(.68,.78),(.58,.78)],p.accent,p.dark,2)
    elif family=='weave':
        for x in np.arange(.37,.67,.017):p.line([(x,.38),(x,.60)],p.main,1)
    elif family in ('engraving','charcoal','cyanotype'):
        for x in np.arange(.38,.67,.013):p.line([(x,.765),(min(x+.035,.67),.74)],p.main,1)


def gate_mark(p):
    """The chosen primary motif changes the focal silhouette, rather than just its label."""
    m=p.spec['motifs'][0]; x=.5;y=.5
    if m in ('iris shutter','locking collar','lens mask'):
        p.ellipse((x-.095,y-.16,x+.095,y+.16),p.dark)
    if m in ('split key','sliding pin','pivot lever','counterweight'):
        angle={'split key':-.3,'sliding pin':0,'pivot lever':.75,'counterweight':1.3}[m]
        dx=.16*math.cos(angle);dy=.19*math.sin(angle)
        p.line([(x-dx,y-dy),(x+dx,y+dy)],p.accent,18)
        p.ellipse((x-.03,y-.05,x+.03,y+.05),p.light)
        if m=='split key':p.rect((x+.04,y+.018,x+.08,y+.13),p.accent)
        if m=='counterweight':p.rect((x+dx-.05,y+dy-.04,x+dx+.05,y+dy+.10),p.light)
    elif m == 'locking collar':
        p.ellipse((x-.14,y-.19,x+.14,y+.19),p.accent,p.light,2)
        p.ellipse((x-.083,y-.115,x+.083,y+.115),p.dark)
        p.rect((x-.02,y-.22,x+.025,y+.22),p.dark)
        p.rect((x-.065,y-.038,x+.080,y+.038),p.light)
    elif m in ('iris shutter','lens mask'):
        for i in range(8):
            a=math.tau*i/8;b=a+.5
            p.poly([(x+.12*math.cos(a),y+.18*math.sin(a)),(x+.12*math.cos(b),y+.18*math.sin(b)),(x+.046*math.cos(b+1),y+.067*math.sin(b+1))],p.accent if i%2 else p.light,p.dark,2)
        if m=='lens mask':p.rect((x-.13,y-.02,x+.13,y+.02),p.dark)
    elif m=='wedge stop':p.poly([(x-.15,y+.12),(x+.15,y+.12),(x+.05,y-.17)],p.accent,p.light,3)
    elif m=='ratchet tooth':
        p.poly([(x-.14,y+.11),(x-.11,y-.08),(x-.02,y-.04),(x+.02,y-.16),(x+.11,y-.11),(x+.14,y+.11)],p.accent,p.light,3)
    elif m=='bridge gap':
        p.rect((x-.17,y-.06,x-.025,y+.06),p.accent);p.rect((x+.04,y-.06,x+.17,y+.06),p.light)
    elif m=='perforated sieve':
        p.rect((x-.12,y-.16,x+.12,y+.16),p.accent,p.light,2)
        for i in range(3):
            for j in range(4):p.ellipse((x-.085+i*.06,y-.125+j*.067,x-.055+i*.06,y-.083+j*.067),p.dark)
    elif m=='forked conduit':p.line([(x,y+.19),(x,y),(x-.13,y-.16)],p.accent,14);p.line([(x,y),(x+.13,y-.16)],p.light,14)
    elif m=='ribbon knot':
        p.curve([(x-.16,y-.10),(x+.19,y-.23),(x-.18,y+.21),(x+.16,y+.11)],p.accent,22)
        p.curve([(x+.16,y-.10),(x-.19,y-.23),(x+.18,y+.21),(x-.16,y+.11)],p.light,12)
    elif m=='hinged door':p.poly([(x-.11,y-.16),(x+.10,y-.11),(x+.10,y+.17),(x-.11,y+.13)],p.accent,p.light,3)
    elif m == 'folded clasp':
        p.poly([(x-.16,y-.13),(x,y-.07),(x,y+.14),(x-.16,y+.07)],p.light,p.dark,2)
        p.poly([(x+.16,y-.13),(x,y-.07),(x,y+.14),(x+.16,y+.07)],p.accent,p.dark,2)
        p.line([(x,y-.07),(x,y+.14)],p.dark,4)
    elif m == 'release buckle':
        p.rect((x-.20,y-.04,x-.065,y+.04),p.main,p.light,2)
        p.rect((x+.075,y-.04,x+.21,y+.04),p.main,p.light,2)
        p.poly([(x-.10,y-.11),(x+.07,y-.11),(x+.12,y-.04),(x+.12,y+.04),(x+.07,y+.11),(x-.10,y+.11)],p.accent,p.light,3)
        p.rect((x-.05,y-.05,x+.045,y+.05),p.dark,p.light,2)
        p.line([(x+.15,y-.07),(x+.15,y+.07)],p.light,3)
    if p.spec['story_binding']['no_target']:
        p.line([(x-.14,y-.19),(x+.14,y+.19)],p.light,4)


def render(spec, layout, destination):
    family=spec['render_family']
    if family not in RENDERERS or spec['style_family'] != STYLES[family][0]:
        raise ValueError('Render family and style label disagree')
    if spec['motifs'][0] not in MOTIFS or spec['palette'] != PALETTES[spec['hue_family']]:
        raise ValueError('Unknown motif or altered palette')
    if spec.get('story_treatment') != story_treatment(spec['story_binding']):
        raise ValueError('Story treatment must follow the verified decision')
    p=Painter(spec,layout['subject_zone']); RENDERERS[family](p);written_artifact(p);gate_mark(p)
    subject=p.layer.resize((SIZE,SIZE),Image.Resampling.LANCZOS)
    # Exact alpha-mask bounds are measured from drawn pixels, including anti-aliasing.
    bbox=subject.getchannel('A').getbbox()
    zone=layout['subject_zone']
    if bbox is None or any((bbox[0]<zone[0],bbox[1]<zone[1],bbox[2]>zone[2],bbox[3]>zone[3])):
        raise ValueError('Rendered subject violates measured typography clearance')
    rng=np.random.default_rng(spec['seed']);bg=np.array(tuple(int(spec['palette'][0][i:i+2],16) for i in (1,3,5)),float)
    yy,xx=np.mgrid[0:SIZE,0:SIZE]; light=np.exp(-(((xx-SIZE*.5)/(SIZE*.60))**2+((yy-SIZE*.45)/(SIZE*.55))**2))
    rgb=np.broadcast_to(bg,(SIZE,SIZE,3)).copy()+light[...,None]*17
    grain=rng.normal(0,1.8,(SIZE,SIZE,1));rgb=np.clip(rgb+grain,0,255).astype('uint8')
    canvas=Image.fromarray(rgb,'RGB').convert('RGBA')
    if family in ('paper_relief','isometric','tiles','ribbons'):
        shadow=Image.new('RGBA',(SIZE,SIZE),(0,0,0,0));shadow.putalpha(subject.getchannel('A').filter(ImageFilter.GaussianBlur(10)))
        canvas.alpha_composite(shadow,(7,10))
    canvas.alpha_composite(subject)
    destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
    canvas.convert('RGB').save(destination,'PNG',optimize=True)
    return {'generator_version':VERSION,'source':'procedural','base_sha256':digest(destination),
            'renderer_sha256':digest(__file__),'subject_box':list(bbox),'seed':spec['seed'],
            'layer_count':len(spec['story_binding']['layers']),'gate_order':spec['story_binding']['gate_order']}


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    choose=sub.add_parser('plan');choose.add_argument('--dossier',required=True,type=Path);choose.add_argument('--history',required=True,type=Path);choose.add_argument('--out',required=True,type=Path);choose.add_argument('--salt',default='')
    draw=sub.add_parser('render');draw.add_argument('--spec',required=True,type=Path);draw.add_argument('--layout',required=True,type=Path);draw.add_argument('--dossier',required=True,type=Path);draw.add_argument('--out',required=True,type=Path);draw.add_argument('--receipt',required=True,type=Path)
    a=p.parse_args()
    if a.command=='plan':
        candidates=plans(json.loads(a.dossier.read_text()),json.loads(a.history.read_text()),salt=a.salt)
        for spec in candidates:spec['dossier_sha256']=digest(a.dossier)
        a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps({'concepts':candidates},indent=2)+'\n')
        print(json.dumps({'plans':str(a.out),'concepts':[{'style':s['style_family'],'composition':s['composition'],'motif':s['motifs'][0]} for s in candidates]}))
    else:
        spec=json.loads(a.spec.read_text())
        if spec.get('dossier_sha256')!=digest(a.dossier) or spec['story_binding']!=story(json.loads(a.dossier.read_text())):
            raise ValueError('Art specification does not bind to this exact verified dossier')
        receipt=render(spec,json.loads(a.layout.read_text()),a.out);receipt['spec_sha256']=digest(a.spec)
        a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))


if __name__=='__main__':main()
