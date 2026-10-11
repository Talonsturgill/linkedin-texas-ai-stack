import base64
import json
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

    def test_native_gmail_multipart_body_and_labels_stay_on_same_message(self):
        encoded=base64.urlsafe_b64encode(('<p>'+self.binding['marker']+'</p>').encode()).decode().rstrip('=')
        row={'labelIds':['DRAFT'],'payload':{
            'mimeType':'multipart/alternative','headers':[{'name':'Subject','value':'Mailbox proof'}],
            'parts':[{'mimeType':'text/html','body':{'data':encoded}}]}}
        self.assertTrue(verify(self.binding,{'message':row}))
        self.assertFalse(verify(self.binding,{'messages':[
            {**row,'labelIds':[]},{'subject':'Other','labelIds':['DRAFT']}]}))
        row['payload']['parts'][0]['body']['data']='%%%invalid%%%'
        self.assertFalse(verify(self.binding,row))

    def test_marker_in_snippet_header_or_another_message_is_not_full_body_proof(self):
        for key in ('snippet','from','to'):
            self.assertFalse(verify(self.binding,{'subject':'Mailbox proof','label_ids':['DRAFT'],
                                                 key:self.binding['marker']}))
        self.assertFalse(verify(self.binding,{'subject':'Mailbox proof','label_ids':['DRAFT'],
                                             'messages':[{**self.readback,'label_ids':[]}]}))

    def test_no_environment_binding_and_public_output_fail(self):
        with self.assertRaises(ValueError):load_binding({})
        with self.assertRaises(ValueError):private_path('out/gmail_binding.json')

    def test_direct_challenge_read_requires_the_bound_message(self):
        binding={**self.binding,'marker_message_id':'challenge-message'}
        for key in ('id','message_id','messageId'):
            self.assertTrue(verify(binding,{**self.readback,key:'challenge-message'}))
        self.assertFalse(verify(binding,self.readback))
        self.assertFalse(verify(binding,{**self.readback,'id':'another-message'}))
        self.assertFalse(verify(binding,{'messages':[
            {**self.readback,'id':'another-message'},
            {'id':'challenge-message','labelIds':['DRAFT']}]}))

    def test_optional_direct_identifier_is_validated_without_exposing_it(self):
        binding={**self.binding,'schema_version':1,
                 'profile_provider':'authenticated_gmail_profile',
                 'recipient':'owner@example.invalid',
                 'profile_verified_at_utc':'2026-10-11T00:00:00Z'}
        for message_id in ('challenge-message','18af020abcd'):
            value={**binding,'marker_message_id':message_id}
            self.assertEqual(load_binding({'TEXAS_STACK_GMAIL_BINDING':json.dumps(value)}),value)
        self.assertEqual(load_binding({'TEXAS_STACK_GMAIL_BINDING':json.dumps(binding)}),binding)
        for message_id in ('',' ',False,3,[], 'https://example.invalid/message', 'a'*513):
            with self.assertRaisesRegex(ValueError,'Private challenge message identifier is invalid'):
                load_binding({'TEXAS_STACK_GMAIL_BINDING':json.dumps({**binding,'marker_message_id':message_id})})


if __name__=='__main__':unittest.main()
