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
    def test_collateral_scene_requires_its_verified_condition_and_cooldowns(self):
        value=dossier();value['selected_mechanism']['chokepoint']['binary_decision']='Accept or reject financial security before study inclusion'
        spec=plans(value,{},preferred_family='collateral_balance')[0]
        self.assertEqual(spec['story_treatment'],'financial_security')
        self.assertEqual(spec['motifs'],['escrow counterweight'])
        for history in ({'artwork_cooldowns':{'primary_motifs_last_10':['escrow counterweight']}},
                        {'artwork_cooldowns':{'style_families_last_8':['machined collateral balance']}}):
            with self.assertRaises(ValueError):plans(value,history,preferred_family='collateral_balance')
        with self.assertRaises(ValueError):plans(dossier(no_target=True),{},preferred_family='collateral_balance')
        with self.assertRaises(ValueError):plans(dossier(),{},preferred_family='collateral_balance')
        spec['motifs']=['pivot lever']
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):render(spec,{'subject_zone':[64,196,1016,700]},Path(temp)/'x.png')

    def test_collateral_scene_has_reproducible_connected_geometry(self):
        value=dossier();value['selected_mechanism']['chokepoint']['binary_decision']='Accept or reject financial security before study inclusion'
        spec=plans(value,{},preferred_family='collateral_balance')[0]
        with tempfile.TemporaryDirectory() as temp:
            a=Path(temp)/'a.png';b=Path(temp)/'b.png';layout={'subject_zone':[64,196,1016,700]}
            receipt=render(spec,layout,a);render(spec,layout,b)
            self.assertEqual(digest(a),digest(b))
            l,t,r,bounds_bottom=receipt['subject_box']
            self.assertTrue(l>=64 and t>=196 and r<=1016 and bounds_bottom<=700)
            other=plans(dossier(no_target=True),{},preferred_family='editorial_scene')[0]
            other['palette']=spec['palette'];other['hue_family']=spec['hue_family'];other['seed']=spec['seed']
            render(other,layout,b)
            self.assertGreaterEqual(distances(fingerprint(a),fingerprint(b))['structure_distance'],.18)

    def test_paired_bay_and_points_scenes_bind_to_a_binary_decision_and_cooldowns(self):
        for family,style,motif in (('bay_wall','paired bay wall study','closed bay'),
                                   ('points_switch','railway points study','thrown points')):
            spec=plans(dossier(),{},preferred_family=family)[0]
            self.assertEqual(spec['render_family'],family);self.assertEqual(spec['motifs'],[motif])
            self.assertEqual(spec['story_treatment'],'binary_gate')
            for history in ({'artwork_cooldowns':{'primary_motifs_last_10':[motif]}},
                            {'artwork_cooldowns':{'style_families_last_8':[style]}}):
                with self.assertRaises(ValueError):plans(dossier(),history,preferred_family=family)
            with self.assertRaises(ValueError):plans(dossier(no_target=True),{},preferred_family=family)
            written=dossier();written['selected_mechanism']['chokepoint']['binary_decision']='Grant or withhold written approval for potable water'
            with self.assertRaises(ValueError):plans(written,{},preferred_family=family)
            spec['motifs']=['pivot lever']
            with tempfile.TemporaryDirectory() as temp:
                with self.assertRaises(ValueError):render(spec,{'subject_zone':[64,196,1016,686]},Path(temp)/'x.png')

    def test_paired_bay_scene_is_reproducible_clear_of_type_and_distinct_from_points(self):
        layout={'subject_zone':[64,196,1016,686]}
        bay=plans(dossier(),{},preferred_family='bay_wall')[0]
        points=plans(dossier(),{},preferred_family='points_switch')[0]
        points['palette']=bay['palette'];points['hue_family']=bay['hue_family'];points['seed']=bay['seed']
        with tempfile.TemporaryDirectory() as temp:
            a=Path(temp)/'a.png';b=Path(temp)/'b.png';c=Path(temp)/'c.png'
            receipt=render(bay,layout,a);render(bay,layout,b);render(points,layout,c)
            self.assertEqual(digest(a),digest(b))
            l,t,r,bottom=receipt['subject_box']
            self.assertTrue(l>=64 and t>=196 and r<=1016 and bottom<=686)
            self.assertGreaterEqual(distances(fingerprint(a),fingerprint(c))['structure_distance'],.18)

    def test_scene_composition_labels_cannot_invent_an_unimplemented_view(self):
        for family,actual in (('bay_wall','low_threshold'),('points_switch','long_approach')):
            spec=plans(dossier(),{},preferred_family=family)[0]
            self.assertEqual(STYLES[family][1],[actual])
            spec['composition']='invented_view'
            with tempfile.TemporaryDirectory() as temp:
                with self.assertRaises(ValueError):render(spec,{'subject_zone':[64,196,1016,686]},Path(temp)/'x.png')

    def test_scene_motif_is_bound_and_cannot_evade_cooldown(self):
        value=dossier();value['selected_mechanism']['chokepoint']['binary_decision']='Grant or withhold written approval for potable water'
        spec=plans(value,{},preferred_family='editorial_scene')[0]
        self.assertEqual(spec['motifs'],['folded document dam'])
        with self.assertRaises(ValueError):
            plans(value,{'artwork_cooldowns':{'primary_motifs_last_10':['folded document dam']}},preferred_family='editorial_scene')
        spec['motifs']=['missing keystone']
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):render(spec,{'subject_zone':[64,196,1016,700]},Path(temp)/'x.png')

    def test_evidence_gap_and_permission_have_different_real_geometry(self):
        target=dossier();target['selected_mechanism']['chokepoint']['binary_decision']='Grant or withhold written approval for potable water'
        one=plans(target,{},preferred_family='editorial_scene')[0]
        two=plans(dossier(no_target=True),{},preferred_family='editorial_scene')[0]
        two['palette']=one['palette'];two['hue_family']=one['hue_family'];two['composition']=one['composition'];two['seed']=one['seed']
        with tempfile.TemporaryDirectory() as temp:
            a=Path(temp)/'a.png';b=Path(temp)/'b.png';layout={'subject_zone':[64,196,1016,700]}
            render(one,layout,a);render(two,layout,b)
            self.assertGreaterEqual(distances(fingerprint(a),fingerprint(b))['structure_distance'],.18)

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
