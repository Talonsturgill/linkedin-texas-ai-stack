import base64
import copy
import hashlib
import json
import sys
import unittest
from email.message import EmailMessage
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from gmail_delivery import extract_result,verify_delivery,VisibleHTML,prepare,delivered_link_target


class GmailDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.url='https://raw.githubusercontent.com/Talonsturgill/linkedin-texas-ai-stack/'+'a'*40+'/out/post_image.png'
        self.body='<html><head><style>p{color:red}</style></head><body><h2>Post</h2><p>Verified full copy.</p><a href="'+self.url+'">Full cover</a><img src="'+self.url+'"></body></html>'
        self.payload={'to':'owner@example.invalid','subject':'Test draft','payload':{'body':{'content':self.body}}}
        self.binding={'verified':True,'recipient':'owner@example.invalid'}
        self.preview={'filename':'texas-stack-preview.jpg','mime_type':'image/jpeg','bytes':3,
                      'sha256':hashlib.sha256(b'jpg').hexdigest()}

    def raw(self,body=None,to='owner@example.invalid',attachment=b'jpg',cc=None):
        message=EmailMessage();message['Subject']='Test draft';message['To']=to
        if cc:message['Cc']=cc
        message.set_content('Full HTML body follows.');message.add_alternative(self.body if body is None else body,subtype='html')
        if attachment is not None:message.add_attachment(attachment,maintype='image',subtype='jpeg',filename=self.preview['filename'])
        return {'id':'draft','messageId':'message','labelIds':['DRAFT'],
                'raw':base64.urlsafe_b64encode(message.as_bytes()).decode().rstrip('=')}

    def records(self,result,*,name='mcp__gmail__get_draft',draft='draft',format='RAW'):
        return [{'message':{'content':[{'type':'tool_use','id':'call','name':name,
                 'input':{'draftId':draft,'messageFormat':format}}]}},
                {'message':{'content':[{'type':'tool_result','tool_use_id':'call','content':json.dumps(result)}]}}]

    def test_extraction_binds_actual_successful_raw_call_and_response(self):
        row=self.raw();records=self.records(row)
        self.assertEqual(extract_result(records,draft_id='draft'),row)
        self.assertEqual(extract_result(records,subject='Test draft'),row)
        for changed in (self.records(row,draft='other'),self.records(row,format='FULL'),
                        self.records(row,name='mcp__gmail__get_message')):
            with self.assertRaises(ValueError):extract_result(changed,draft_id='draft')
        records[-1]['message']['content'][0]['is_error']=True
        with self.assertRaises(ValueError):extract_result(records,draft_id='draft')

    def test_extraction_reads_wrapped_tool_text_and_rejects_wrong_subject_or_errors(self):
        row=self.raw();wrapped={'content':[{'type':'text','text':json.dumps(row)}]}
        self.assertEqual(extract_result(self.records(wrapped),subject='Test draft'),row)
        with self.assertRaises(ValueError):extract_result(self.records(row),subject='Another issue')
        with self.assertRaises(ValueError):extract_result(self.records({'isError':True,'content':[row]}),draft_id='draft')

    def test_complete_html_and_exact_preview_pass(self):
        report=verify_delivery(self.payload,self.binding,self.raw(),self.preview)
        self.assertTrue(report['ok']);self.assertTrue(report['exact_html_bytes_match'])
        self.assertTrue(report['inline_cover_retained'])

    def test_connector_sanitization_requires_complete_text_links_and_preview(self):
        sanitized='<h2>Post</h2><p>Verified full copy.</p><a href="'+self.url+'">Full cover</a>'
        report=verify_delivery(self.payload,self.binding,self.raw(sanitized),self.preview)
        self.assertTrue(report['ok']);self.assertTrue(report['markup_sanitized'])
        self.assertFalse(report['inline_cover_retained'])
        for changed in (sanitized.replace('Verified full copy.','Partial copy.'),
                        sanitized.replace(self.url,'https://example.invalid/missing')):
            self.assertFalse(verify_delivery(self.payload,self.binding,self.raw(changed),self.preview)['ok'])
        self.assertFalse(verify_delivery(self.payload,self.binding,self.raw(sanitized,attachment=None),self.preview)['ok'])

    def test_draft_recipient_extra_recipient_and_attachment_are_checked(self):
        for changed in (self.raw(to='other@example.invalid'),self.raw(cc='other@example.invalid'),
                        self.raw(attachment=b'bad'),self.raw(attachment=None)):
            self.assertFalse(verify_delivery(self.payload,self.binding,changed,self.preview)['ok'])
        changed=self.raw();changed['labelIds'].append('SENT')
        self.assertFalse(verify_delivery(self.payload,self.binding,changed,self.preview)['ok'])
        self.assertFalse(verify_delivery(self.payload,{**self.binding,'verified':False},self.raw(),self.preview)['ok'])

    def test_preview_packet_is_small_and_has_no_recipient_field(self):
        from PIL import Image
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            image=Path(directory)/'cover.png';Image.new('RGB',(1080,1080),(70,35,120)).save(image)
            packet,proof=prepare(self.payload,image)
        self.assertEqual((proof['width'],proof['height']),(160,160))
        data=base64.b64decode(packet['attachments'][0]['content'],validate=True)
        self.assertEqual(len(data),proof['bytes']);self.assertLessEqual(len(data),4096)
        self.assertEqual(hashlib.sha256(data).hexdigest(),proof['sha256'])
        self.assertNotIn('to',packet);self.assertNotIn('toRecipients',packet)
        self.assertEqual(packet['bodyHtml'],self.body)

    def test_normal_daily_connector_path_has_no_encoded_attachment_and_requires_cover_link(self):
        packet,proof=prepare(self.payload)
        self.assertIsNone(proof);self.assertNotIn('attachments',packet)
        self.assertEqual(packet,{'subject':'Test draft','bodyHtml':self.body})
        sanitized='<h2>Post</h2><p>Verified full copy.</p><a href="'+self.url+'">Full cover</a>'
        report=verify_delivery(self.payload,self.binding,self.raw(sanitized,attachment=None))
        self.assertTrue(report['ok']);self.assertEqual(report['delivery_image_mode'],'immutable_full_cover_link')
        missing=sanitized.replace(self.url,'https://example.invalid/missing')
        self.assertFalse(verify_delivery(self.payload,self.binding,self.raw(missing,attachment=None))['ok'])

    def test_gmail_google_wrapper_must_preserve_exact_original_target(self):
        wrapped='https://www.google.com/url?q='+quote(self.url,safe='')+'&sa=D&source=editors'
        body='<h2>Post</h2><p>Verified full copy.</p><a href="'+wrapped+'">Full cover</a>'
        report=verify_delivery(self.payload,self.binding,self.raw(body,attachment=None))
        self.assertTrue(report['ok']);self.assertEqual(report['google_wrapped_link_count'],1)
        wrong=wrapped.replace(quote(self.url,safe=''),quote(self.url.replace('a'*40,'b'*40),safe=''))
        self.assertFalse(verify_delivery(self.payload,self.binding,self.raw(body.replace(wrapped,wrong),attachment=None))['ok'])

    def test_link_wrapper_cannot_accept_other_hosts_schemes_duplicate_targets_or_missing_q(self):
        for href in ('http://www.google.com/url?q='+quote(self.url,safe=''),
                     'https://google.com.evil.invalid/url?q='+quote(self.url,safe=''),
                     'https://www.google.com@evil.invalid/url?q='+quote(self.url,safe=''),
                     'https://www.google.com/url?q='+quote(self.url,safe='')+'&q=https://evil.invalid',
                     'https://www.google.com/url?url='+quote(self.url,safe=''),
                     'https://www.google.com/url?q=javascript:alert(1)'):
            self.assertEqual(delivered_link_target(href),href)


if __name__=='__main__':unittest.main()
