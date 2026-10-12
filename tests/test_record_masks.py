import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.agents/skills/texas-stack-artwork/scripts'))
from procedural_art import plans,render,digest
from variety_check import fingerprint,distances
from test_pipeline import dossier


def records():
    value=dossier()
    value['selected_mechanism']['name']='Geographic record disclosure gate'
    value['selected_mechanism']['chokepoint']['binary_decision']='Release or withhold county and regional water planning fields'
    return value


class RecordMaskTests(unittest.TestCase):
    def test_both_verified_fields_and_unused_motif_are_required(self):
        spec=plans(records(),{},preferred_family='record_masks')[0]
        self.assertEqual(spec['motifs'],['paired location masks'])
        self.assertEqual(spec['composition'],'oblique_folio')
        for value in (dossier(),dossier(no_target=True)):
            with self.assertRaises(ValueError):plans(value,{},preferred_family='record_masks')
        one=records();one['selected_mechanism']['chokepoint']['binary_decision']='Release or withhold county fields'
        with self.assertRaises(ValueError):plans(one,{},preferred_family='record_masks')
        for history in (
            {'artwork_cooldowns':{'primary_motifs_last_10':['paired location masks']}},
            {'artwork_cooldowns':{'style_families_last_8':['brushed-metal record masking study']}},
            {'artwork_cooldowns':{'compositions_last_2':['oblique_folio']}}
        ):
            with self.assertRaises(ValueError):plans(records(),history,preferred_family='record_masks')

    def test_fixture_is_reproducible_clear_of_type_and_structurally_distinct(self):
        spec=plans(records(),{},preferred_family='record_masks',preferred_hue='celadon_red')[0]
        other=plans(dossier(),{},preferred_family='bay_wall')[0]
        other['palette']=spec['palette'];other['hue_family']=spec['hue_family'];other['seed']=spec['seed']
        with tempfile.TemporaryDirectory() as temp:
            first=Path(temp)/'synthetic-a.png';again=Path(temp)/'synthetic-b.png';prior=Path(temp)/'synthetic-prior.png'
            layout={'subject_zone':[64,196,1016,686]}
            receipt=render(spec,layout,first);render(spec,layout,again);render(other,layout,prior)
            self.assertEqual(digest(first),digest(again))
            left,top,right,bottom=receipt['subject_box']
            self.assertTrue(left>=64 and top>=196 and right<=1016 and bottom<=686)
            self.assertGreaterEqual(distances(fingerprint(first),fingerprint(prior))['structure_distance'],.18)
            self.assertEqual(receipt['render_kind'],'fixture')

    def test_scene_and_motif_cannot_be_relabelled(self):
        valid=plans(records(),{},preferred_family='record_masks')[0]
        other=plans(records(),{},preferred_family='charcoal')[0]
        with tempfile.TemporaryDirectory() as temp:
            for spec in (dict(valid,motifs=['sliding pin']),
                         dict(other,motifs=['paired location masks']),
                         dict(valid,composition='invented_view')):
                with self.assertRaises(ValueError):render(spec,{'subject_zone':[64,196,1016,686]},Path(temp)/'synthetic.png')


if __name__=='__main__':unittest.main()
