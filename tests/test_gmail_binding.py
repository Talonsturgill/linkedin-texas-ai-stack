import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from gmail_binding import verify,private_path,load_binding


class BindingTests(unittest.TestCase):
    def setUp(self):
        self.binding={'marker_subject':'Mailbox proof','marker':'0123456789abcdef0123456789abcdef'}
        self.readback={'subject':'Mailbox proof','body_html':'<p>'+self.binding['marker']+'</p>','label_ids':['DRAFT']}

    def test_challenge_needs_full_marker_subject_and_draft_labels(self):
        self.assertTrue(verify(self.binding,{'result':[self.readback]}))
        for key in ('subject','body_html','label_ids'):
            row=dict(self.readback);row.pop(key)
            self.assertFalse(verify(self.binding,row))
        self.assertFalse(verify(self.binding,{**self.readback,'label_ids':['DRAFT','SENT']}))
        self.assertFalse(verify(self.binding,{'emails':[
            {**self.readback,'label_ids':[]},{'subject':'Other draft','label_ids':['DRAFT']}]}))

    def test_sender_or_recipient_cannot_verify_identity(self):
        self.assertFalse(verify(self.binding,{'to':'owner@example.invalid','from':'owner@example.invalid','label_ids':['DRAFT']}))
        self.assertFalse(verify(self.binding,{**self.readback,'body_html':'different marker'}))

    def test_no_environment_binding_and_public_output_fail(self):
        with self.assertRaises(ValueError):load_binding({})
        with self.assertRaises(ValueError):private_path('out/gmail_binding.json')


if __name__=='__main__':unittest.main()
