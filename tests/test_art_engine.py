from __future__ import annotations
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'.agents/skills/texas-stack-artwork/scripts'
sys.path.insert(0,str(ART));sys.path.insert(0,str(ROOT/'scripts'))
import art_layout
import compose_cover
import qa_check
import review_art
import build_email
from test_pipeline import dossier,valid_post,art_eval


class ArtEngineTests(unittest.TestCase):
    def test_bundled_fonts_are_verified_without_network_or_host_fallback(self):
        with patch('urllib.request.urlopen',side_effect=AssertionError('Network should not be needed')):
            pair=compose_cover.font_pair()
        self.assertTrue(all(Path(x).parent==compose_cover.FONT_DIR for x in pair))
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);(folder/'manifest.json').write_text((compose_cover.FONT_DIR/'manifest.json').read_text())
            with patch.object(compose_cover,'FONT_DIR',folder):
                with self.assertRaises(RuntimeError):compose_cover.font_pair()

    @classmethod
    def setUpClass(cls):
        # Use the runtime's local fonts; tests never download fonts.
        cls.serif=next((p for p in compose_cover.FALLBACK_SERIF if Path(p).exists()),None)
        cls.mono=next((p for p in compose_cover.FALLBACK_MONO if Path(p).exists()),None)
        if not cls.serif or not cls.mono:raise unittest.SkipTest('local test fonts unavailable')

    def test_headlines_fit_and_leave_actual_clearance(self):
        for title in ['THE AUDIT NOW HOLDS THE PERMIT','WHO CONTROLS THE NEXT CONNECTION','NO DEFENSIBLE TARGET THIS WEEK','CAPITAL FOLLOWS A DIFFERENT PATH']:
            layout=art_layout.headline_layout(title,self.serif)
            self.assertEqual(' '.join(layout['lines']),title)
            self.assertGreaterEqual(layout['font_size'],72)
            self.assertLessEqual(layout['subject_zone'][3]+40,layout['headline_top'])
            for box in layout['text_boxes']:
                self.assertGreaterEqual(box[0],64);self.assertLessEqual(box[2],1016)
                self.assertLessEqual(box[3],939)
        with self.assertRaises(ValueError):art_layout.headline_layout('A'*100+' THREE MORE WORDS',self.serif)

    def test_collision_is_rejected_instead_of_hiding_the_subject(self):
        layout=art_layout.headline_layout('THE AUDIT NOW HOLDS THE PERMIT',self.serif)
        art_layout.validate_subject_box([100,240,900,layout['subject_zone'][3]],layout)
        for box in ([100,240,900,layout['headline_top']],[-1,240,900,500],[100,50,900,500]):
            with self.assertRaises(ValueError):art_layout.validate_subject_box(box,layout)

    def test_generated_bytes_review_and_metadata_stay_bound(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);base=p/'base.png';cover=p/'cover.png';ev=p/'eval.json';prompt=p/'prompt.txt';plan=p/'plan.md'
            Image.new('RGB',(1080,1080),'#534764').save(base)
            prompt.write_text('A source grounded scene.');plan.write_text('Measured layout.')
            a=art_eval();a.update(concepts=['a','b','c'],selected_concept='a',style_family='paper',palette=['#534764','#ffffff'],hue_family='violet',composition='central_apparatus',motifs=['subject'],eval_history=[],eval_final={})
            ev.write_text(json.dumps(a))
            args=dict(base_path=base,headline='THE AUDIT NOW HOLDS THE PERMIT',category='REGULATORY',date='September 25th, 2026',place='TEXAS',prompt_file=prompt,plan_file=plan,eval_file=ev,out_path=cover,subject_box=[100,240,900,600])
            with patch.object(compose_cover,'font_pair',return_value=(self.serif,self.mono)):
                compose_cover.compose(**args)
                before=qa_check.sha256(cover)
                review=p/'review.json';review.write_text(json.dumps(dict(scores={k:9 for k in qa_check.WEIGHTS},notes={k:'Observed in the test fixture.' for k in qa_check.WEIGHTS},inspected_scales=['full','300'],blockers=[])))
                review_art.record(ev,review,base,cover,True)
                compose_cover.compose(**args)
                self.assertEqual(qa_check.sha256(cover),before)
            errors=qa_check.validate(cover,base,prompt,plan,ev,args['date'],'THE TEXAS STACK')
            # The flat test fixture is deliberately below the production file-size minimum.
            self.assertFalse(any('review' in e or 'metadata' in e or 'subject' in e for e in errors),errors)
            with self.assertRaises(ValueError):review_art.record(ev,review,base,cover,True)
            review_art.record(ev,review,base,cover,True,replace_pass=1)
            self.assertEqual(len(json.loads(ev.read_text())['eval_history']),1)
            im=Image.open(cover);ImageDraw.Draw(im).rectangle((0,0,20,20),fill='red');im.save(cover)
            errors=qa_check.validate(cover,base,prompt,plan,ev,args['date'],'THE TEXAS STACK')
            self.assertTrue(any('different image bytes' in e for e in errors))
            transparent=Image.new('RGBA',(1080,1080),(0,0,0,0));transparent.save(base)
            with patch.object(compose_cover,'font_pair',return_value=(self.serif,self.mono)):
                with self.assertRaisesRegex(ValueError,'transparency'):compose_cover.compose(**args)

    def test_high_scores_cannot_select_visual_blockers(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);ev=p/'eval.json';rev=p/'review.json';base=p/'base.png';cover=p/'cover.png'
            ev.write_text(json.dumps({'eval_history':[]}));base.write_bytes(b'base');cover.write_bytes(b'cover')
            review=dict(scores={k:9.8 for k in qa_check.WEIGHTS},notes={k:'Observed strength.' for k in qa_check.WEIGHTS},inspected_scales=['full','300'],blockers=['Invented label'])
            rev.write_text(json.dumps(review))
            with self.assertRaisesRegex(ValueError,'blockers'):review_art.record(ev,rev,base,cover,True)
            review['blockers']=[];review['scores']['concept']=float('nan');rev.write_text(json.dumps(review))
            with self.assertRaisesRegex(ValueError,'finite'):review_art.record(ev,rev,base,cover,True)

    def test_development_fixture_cannot_be_promoted_by_high_scores(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);base=p/'art_base.png';cover=p/'post_image.png'
            Image.new('RGB',(1080,1080),'#534764').save(base);base_bytes=base.read_bytes();cover.write_bytes(base_bytes)
            prompt=p/'image_prompt.txt';plan=p/'art_plan.md';ev=p/'art_eval.json'
            prompt.write_text('Synthetic fixture');plan.write_text('Development only')
            evaluation=art_eval();evaluation['source']='procedural';ev.write_text(json.dumps(evaluation))
            Path(str(cover)+'.meta.json').write_text('{}')
            for name,value in (('art_spec.json',{}),('art_variety.json',{}),('stack_anatomy.json',dossier()),
                               ('art_render.json',{'generator_version':5,'render_kind':'fixture'})):
                (p/name).write_text(json.dumps(value))
            errors=qa_check.validate(cover,base,prompt,plan,ev,'September 25th, 2026','THE TEXAS STACK')
            self.assertIn('development fixtures cannot become production covers',errors)

    def test_email_sections_follow_delivery_contract(self):
        html=build_email.render_html(post=valid_post(),image_url='https://example.com/image.png',dossier=dossier(),score={'criteria':[{'name':'Hook','score':9,'weight':1,'notes':'Clear'}]},art_eval=art_eval(),date='date',branch='branch',commit='commit',editor_note='Review this.')
        order=['Copy this for LinkedIn','class="image"','<h2>Sources','Editorial report card','<h2>Artwork evaluation','<b>Editor note','class="foot"']
        positions=[html.index(x) for x in order];self.assertEqual(positions,sorted(positions))
        self.assertEqual(html.count('<img '),1)

    def test_email_preserves_native_editorial_notes_and_every_art_dimension(self):
        art=art_eval();art['eval_final']['notes']={k:f'Observed {k} <detail>' for k in art['eval_final']['scores']}
        rows=[{'name':'Hook','score':9,'weight':.5,'note':'Native singular evidence'},
              {'name':'Clarity','score':8,'weight':.5,'notes':'Canonical plural evidence'}]
        args=dict(post=valid_post(),image_url='https://example.com/image.png',dossier=dossier(),score={'criteria':rows},art_eval=art,date='date',branch='branch',commit='commit',editor_note='Review this.')
        body=build_email.render_html(**args)
        for text in ('Native singular evidence','Canonical plural evidence',*[f'Observed {k} &lt;detail&gt;' for k in art['eval_final']['scores']]):
            self.assertIn(text,body)
        rows[0].pop('note')
        with self.assertRaisesRegex(ValueError,'recorded evidence note'):build_email.render_html(**args)

if __name__=='__main__':unittest.main()
