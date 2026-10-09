import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.agents/skills/texas-stack-artwork/scripts'))
from procedural_art import STYLES, PALETTES, MOTIFS, plans, render, story, story_treatment, digest
from variety_check import fingerprint, distances, validate
from test_pipeline import dossier


def prior(spec, image):
    return {**{k:spec[k] for k in ('style_family','hue_family','composition','motifs')},
            'branch':'prior','base_sha256':digest(image),'visual_fingerprint':fingerprint(image)}


class ProceduralTests(unittest.TestCase):
    def test_story_direction_preferences_cannot_override_cooldowns(self):
        candidates=plans(dossier(),{},preferred_family='volume',preferred_hue='glacier_tangerine',preferred_motif='sliding pin')
        self.assertEqual(candidates[0]['render_family'],'volume')
        self.assertEqual(candidates[0]['hue_family'],'glacier_tangerine')
        with self.assertRaises(ValueError):
            plans(dossier(),{'artwork_cooldowns':{'style_families_last_8':['illuminated volume study']}},preferred_family='volume')
        with self.assertRaises(ValueError):
            plans(dossier(),{'artwork_cooldowns':{'hue_families_last_4':['glacier_tangerine']}},preferred_hue='glacier_tangerine')
    def test_long_run_preserves_every_cooldown(self):
        records=[]
        for week in range(60):
            history={'artwork_cooldowns':{
                'style_families_last_8':[s['style_family'] for s in records[:8]],
                'hue_families_last_4':[s['hue_family'] for s in records[:4]],
                'compositions_last_2':[s['composition'] for s in records[:2]],
                'primary_motifs_last_10':[s['motifs'][0] for s in records[:10]]}}
            candidates=plans(dossier(),history,salt=str(week))
            self.assertEqual(len({s['render_family'] for s in candidates}),3)
            self.assertEqual(len({s['composition'] for s in candidates}),3)
            self.assertEqual(len({s['motifs'][0] for s in candidates}),3)
            spec=candidates[0]
            for field,key in [('style_family','style_families_last_8'),('hue_family','hue_families_last_4'),('composition','compositions_last_2')]:
                self.assertNotIn(spec[field],history['artwork_cooldowns'][key])
            self.assertNotIn(spec['motifs'][0],history['artwork_cooldowns']['primary_motifs_last_10'])
            records.insert(0,spec)

    def test_legacy_style_alias_cannot_evade_cooldown(self):
        history={'artwork_cooldowns':{'style_families_last_8':['layered-paper relief','clay/plaster systems-model']}}
        for spec in plans(dossier(),history):self.assertNotIn(spec['render_family'],('paper_relief','tiles'))

    def test_gate_binds_to_real_layer_and_no_target_is_distinct(self):
        value=dossier();value['selected_mechanism']['chokepoint']['layer_order']=9
        with self.assertRaises(ValueError):story(value)
        binding=story(dossier(no_target=True))
        self.assertTrue(binding['no_target']);self.assertEqual(binding['layers'],[])

    def test_written_artifact_requires_a_verified_written_decision(self):
        binding=story(dossier())
        self.assertEqual(story_treatment(binding),'binary_gate')
        binding['decision']='Grant or withhold written approval for temporary emergency potable-water use'
        self.assertEqual(story_treatment(binding),'written_authorization')
        self.assertEqual(story_treatment(story(dossier(no_target=True))),'incomplete_evidence')

    def test_render_is_reproducible_and_respects_type_clearance(self):
        spec=plans(dossier(),{})[0];layout={'subject_zone':[64,196,1016,700]}
        with tempfile.TemporaryDirectory() as temp:
            one=Path(temp)/'one.png';two=Path(temp)/'two.png'
            receipt=render(spec,layout,one);render(spec,layout,two)
            self.assertEqual(digest(one),digest(two))
            l,t,r,b=receipt['subject_box'];self.assertTrue(l>=64 and t>=196 and r<=1016 and b<=700)
            with Image.open(one) as image:self.assertEqual(image.size,(1080,1080));self.assertEqual(image.mode,'RGB')

    def test_duplicate_pixels_fail_despite_new_style_labels(self):
        spec=plans(dossier(),{})[0];layout={'subject_zone':[64,196,1016,700]}
        with tempfile.TemporaryDirectory() as temp:
            image=Path(temp)/'image.png';render(spec,layout,image)
            previous=prior(spec,image);other=plans(dossier(),{},salt='changed')[0]
            report=validate(other,{'recent_artwork':[previous]},image)
            self.assertFalse(report['ok']);self.assertTrue(any('structure' in e for e in report['errors']))

    def test_surface_noise_does_not_fake_structural_novelty(self):
        spec=plans(dossier(),{})[0];layout={'subject_zone':[64,196,1016,700]}
        with tempfile.TemporaryDirectory() as temp:
            one=Path(temp)/'one.png';two=Path(temp)/'two.png';render(spec,layout,one)
            pixels=np.asarray(Image.open(one)).astype(float)
            pixels+=np.random.default_rng(8).normal(0,2,pixels.shape)
            Image.fromarray(np.clip(pixels,0,255).astype('uint8')).save(two)
            self.assertLess(distances(fingerprint(one),fingerprint(two))['structure_distance'],.18)

    def test_render_cannot_be_relabelled(self):
        spec=plans(dossier(),{})[0];spec['style_family']='new name for an old family'
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):render(spec,{'subject_zone':[64,196,1016,700]},Path(temp)/'x.png')


if __name__=='__main__':unittest.main()
