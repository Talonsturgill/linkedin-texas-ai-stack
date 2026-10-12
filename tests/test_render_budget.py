import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'.agents/skills/texas-stack-artwork/scripts'))
from render_budget import reserve,finish,rebind


class RenderBudgetTests(unittest.TestCase):
    def test_failures_and_changed_concepts_do_not_reset_the_six_total(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'budget.json'
            for i in range(1,7):
                self.assertEqual(reserve(path,'issue',f'spec-{i}',f'renderer-{i}'),i)
                finish(path,'issue',i,base_hash='pixels' if i%2 else None,error_type='ValueError' if i%2==0 else None)
            with self.assertRaises(ValueError):reserve(path,'issue','new-concept','new-source')
            self.assertEqual(len(json.loads(path.read_text())['attempts']),6)

    def test_an_interrupted_reservation_is_spent_and_cannot_be_reused(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'budget.json';reserve(path,'issue','spec','renderer')
            self.assertEqual(reserve(path,'issue','spec','renderer'),2)
            finish(path,'issue',2,base_hash='pixels')
            with self.assertRaises(ValueError):finish(path,'issue',2,base_hash='other')

    def test_wrong_branch_or_corrupt_state_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'budget.json';reserve(path,'issue','spec','renderer')
            with self.assertRaises(ValueError):reserve(path,'other','spec','renderer')
            path.write_text('{"schema_version":1,"branch":"issue","limit":6,"attempts":[{}]}')
            with self.assertRaises(ValueError):reserve(path,'issue','spec','renderer')

    def test_evidence_rebind_cannot_change_pixels_layout_or_visual_specification(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'budget.json'
            reserve(path,'issue','old-spec','renderer',layout_hash='layout',visual_spec_hash='visual')
            finish(path,'issue',1,base_hash='pixels')
            inputs=dict(base_hash='pixels',spec_hash='new-spec',renderer_hash='renderer',layout_hash='layout',visual_spec_hash='visual')
            value=rebind(path,'issue',1,**inputs)
            self.assertEqual(len(value['attempts']),1)
            self.assertEqual(value['attempts'][0]['spec_sha256'],'new-spec')
            for key in ('base_hash','renderer_hash','layout_hash','visual_spec_hash'):
                with self.assertRaises(ValueError):rebind(path,'issue',1,**{**inputs,key:'changed'})

    def test_invalid_numbers_cannot_finalize_or_rebind_another_reservation(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'budget.json';reserve(path,'issue','spec','renderer')
            original=path.read_bytes()
            for number in (0,-1,True,'1',2):
                with self.subTest(number=number),self.assertRaises(ValueError):
                    finish(path,'issue',number,base_hash='pixels')
                with self.subTest(number=number),self.assertRaises(ValueError):
                    rebind(path,'issue',number,base_hash='pixels',spec_hash='s',renderer_hash='r',layout_hash='l',visual_spec_hash='v')
                self.assertEqual(path.read_bytes(),original)
