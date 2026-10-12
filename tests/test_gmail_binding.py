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

    def test_google_mcp_thread_keeps_full_body_id_and_labels_on_the_same_message(self):
        binding={**self.binding,'marker_message_id':'bound-message','marker_thread_id':'bound-thread'}
        for key in ('htmlBody','plaintextBody'):
            message={'id':'bound-message','subject':'Mailbox proof',
                     key:'<p>'+binding['marker']+'</p>','labelIds':['DRAFT']}
            self.assertTrue(verify(binding,{'id':'bound-thread','messages':[message]}))
            self.assertFalse(verify(binding,{'id':'bound-thread','messages':[
                {**message,'id':'another-message'},
                {'id':'bound-message','subject':'Mailbox proof','labelIds':['DRAFT']}]}))
            self.assertFalse(verify(binding,{**message,'labelIds':['DRAFT','SENT']}))
            metadata={k:v for k,v in message.items() if k!=key}
            self.assertFalse(verify(binding,{**metadata,'snippet':binding['marker']}))

    def test_thread_reference_requires_an_explicit_valid_message_reference(self):
        binding={**self.binding,'schema_version':1,
                 'profile_provider':'authenticated_gmail_profile','recipient':'owner@example.invalid',
                 'profile_verified_at_utc':'2026-10-11T00:00:00Z','marker_thread_id':'bound-thread'}
        with self.assertRaisesRegex(ValueError,'requires the bound message identifier'):
            load_binding({'TEXAS_STACK_GMAIL_BINDING':json.dumps(binding)})
        binding['marker_message_id']='bound-message'
        self.assertEqual(load_binding({'TEXAS_STACK_GMAIL_BINDING':json.dumps(binding)}),binding)
        for thread_id in ('',' ',False,3,[], 'https://example.invalid/thread','a'*513):
            with self.assertRaisesRegex(ValueError,'Private challenge thread identifier is invalid'):
                load_binding({'TEXAS_STACK_GMAIL_BINDING':json.dumps({**binding,'marker_thread_id':thread_id})})

    def test_actual_claude_raw_draft_binds_both_resource_identifiers(self):
        binding={**self.binding,'marker_draft_id':'r-bound-draft','marker_message_id':'bound-message'}
        mime=('Subject: Mailbox proof\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n'
              '<p>'+binding['marker']+'</p>')
        raw=base64.urlsafe_b64encode(mime.encode()).decode().rstrip('=')
        row={'id':'r-bound-draft','messageId':'bound-message','labelIds':['DRAFT'],'raw':raw}
        self.assertTrue(verify(binding,row))
        self.assertTrue(verify(binding,{'id':'r-bound-draft','message':{
            'id':'bound-message','labelIds':['DRAFT'],'raw':raw}}))
        for change in ({'id':'other-draft'},{'messageId':'other-message'},
                       {'labelIds':['DRAFT','SENT']},{'raw':'%%%invalid%%%'}):
            self.assertFalse(verify(binding,{**row,**change}))
        self.assertFalse(verify(binding,{'drafts':[
            {**row,'id':'other-draft'}, {'id':'r-bound-draft','labelIds':['DRAFT']}]}))
        self.assertFalse(verify(binding,{'id':'r-bound-draft','message':{
            'id':'bound-message','labelIds':[],'raw':raw},'labelIds':['DRAFT']}))

    def test_raw_challenge_rejects_header_attachment_and_metadata_only_proof(self):
        binding={**self.binding,'marker_draft_id':'draft','marker_message_id':'message'}
        row={'id':'draft','messageId':'message','labelIds':['DRAFT']}
        bodies=[
            'Subject: Mailbox proof\r\nX-Marker: '+binding['marker']+'\r\n\r\nOther body',
            'Subject: Mailbox proof\r\nContent-Type: text/plain\r\n'
            'Content-Disposition: attachment; filename="proof.txt"\r\n\r\n'+binding['marker'],
            'Subject: Other subject\r\n\r\n'+binding['marker'],
        ]
        for mime in bodies:
            raw=base64.urlsafe_b64encode(mime.encode()).decode()
            self.assertFalse(verify(binding,{**row,'raw':raw,'subject':'Mailbox proof',
                                            'body_html':binding['marker']}))
        self.assertFalse(verify(binding,{**row,'subject':'Mailbox proof','snippet':binding['marker']}))

    def test_draft_reference_is_validated_and_requires_bound_message(self):
        binding={**self.binding,'schema_version':1,'profile_provider':'authenticated_gmail_profile',
                 'recipient':'owner@example.invalid','profile_verified_at_utc':'2026-10-11T00:00:00Z',
                 'marker_draft_id':'r-draft'}
        with self.assertRaisesRegex(ValueError,'requires the bound message identifier'):
            load_binding({'TEXAS_STACK_GMAIL_BINDING':json.dumps(binding)})
        binding['marker_message_id']='message'
        self.assertEqual(load_binding({'TEXAS_STACK_GMAIL_BINDING':json.dumps(binding)}),binding)
        for draft_id in ('',' ',False,3,[], 'https://example.invalid/draft','a'*513):
            with self.assertRaisesRegex(ValueError,'Private challenge draft identifier is invalid'):
                load_binding({'TEXAS_STACK_GMAIL_BINDING':json.dumps({**binding,'marker_draft_id':draft_id})})

    def test_raw_routing_value_must_match_independently_verified_recipient(self):
        binding={**self.binding,'marker_draft_id':'draft','marker_message_id':'message',
                 'recipient':'owner@example.invalid'}
        for to,expected in (('owner@example.invalid',True),('other@example.invalid',False),
                            ('owner@example.invalid, other@example.invalid',False),('',False)):
            mime=('Subject: Mailbox proof\r\nTo: '+to+'\r\nContent-Type: text/plain\r\n\r\n'+binding['marker'])
            raw=base64.urlsafe_b64encode(mime.encode()).decode()
            row={'id':'draft','messageId':'message','labelIds':['DRAFT'],'raw':raw}
            self.assertEqual(verify(binding,row),expected)


if __name__=='__main__':unittest.main()
