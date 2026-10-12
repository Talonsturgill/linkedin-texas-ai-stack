import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'.agents/skills/texas-stack-artwork/scripts'))
import procedural_art
import render_budget
from test_pipeline import dossier


class RenderCLITests(unittest.TestCase):
    def prepare(self,root):
        value=dossier();spec=procedural_art.plans(value,{})[0]
        paths={name:root/(name+'.json') for name in ('dossier','spec','layout','receipt')}
        paths['out']=root/'base.png'
        paths['dossier'].write_text(json.dumps(value))
        spec['dossier_sha256']=procedural_art.digest(paths['dossier'])
        paths['spec'].write_text(json.dumps(spec))
        paths['layout'].write_text(json.dumps({'subject_zone':[64,196,1016,700]}))
        return paths,value,spec

    def call(self,paths,*extra):
        args=['procedural_art.py','render']
        for name,path in paths.items():args.extend(['--'+name,str(path)])
        with patch.object(sys,'argv',args+list(extra)),contextlib.redirect_stdout(io.StringIO()):
            procedural_art.main()

    def fake_draw(self,spec,layout,destination):
        destination.write_bytes(b'unchanged test pixels')
        return {'generator_version':5,'render_kind':'fixture',
                'renderer_sha256':procedural_art.digest(procedural_art.__file__),
                'base_sha256':procedural_art.digest(destination)}

    def test_cli_counts_failed_calls_and_rejects_a_seventh_before_drawing(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);paths,_,_=self.prepare(root);ledger=root/'budget.json'
            def draw(spec,layout,destination):
                if len(json.loads(ledger.read_text())['attempts'])==3:raise ValueError('clearance failed')
                return self.fake_draw(spec,layout,destination)
            with patch.object(render_budget,'production_ledger',return_value=(ledger,'test-issue')),patch.object(procedural_art,'render',side_effect=draw) as renderer:
                for number in range(1,7):
                    if number==3:
                        with self.assertRaisesRegex(ValueError,'clearance failed'):self.call(paths)
                    else:self.call(paths)
                self.assertEqual(renderer.call_count,6)
                with self.assertRaisesRegex(ValueError,'Six render reservations'):self.call(paths)
                self.assertEqual(renderer.call_count,6)
            budget=json.loads((root/'art_budget.json').read_text())
            self.assertEqual(len(budget['attempts']),6)
            self.assertEqual(budget['attempts'][2]['status'],'failed')
            self.assertEqual(json.loads(paths['receipt'].read_text())['render_kind'],'production')

    def test_cli_rebinds_evidence_urls_without_drawing_and_rejects_scene_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);paths,value,spec=self.prepare(root);ledger=root/'budget.json'
            with patch.object(render_budget,'production_ledger',return_value=(ledger,'test-issue')),patch.object(procedural_art,'render',side_effect=self.fake_draw):
                self.call(paths)
            original=paths['out'].read_bytes()
            value['selected_mechanism']['layers'][0]['primary_source']['url']='https://example.com/actual-official-document'
            paths['dossier'].write_text(json.dumps(value))
            spec['story_binding']=procedural_art.story(value)
            spec['dossier_sha256']=procedural_art.digest(paths['dossier']);paths['spec'].write_text(json.dumps(spec))
            with patch.object(render_budget,'production_ledger',return_value=(ledger,'test-issue')),patch.object(procedural_art,'render',side_effect=AssertionError('Rebinding must not draw')):
                self.call(paths,'--rebind')
                spec['seed']+=1;paths['spec'].write_text(json.dumps(spec))
                with self.assertRaisesRegex(ValueError,'unchanged pixels'):self.call(paths,'--rebind')
            self.assertEqual(paths['out'].read_bytes(),original)
            budget=json.loads(ledger.read_text());self.assertEqual(len(budget['attempts']),1)
            self.assertEqual(len(budget['attempts'][0]['rebind_history']),1)
