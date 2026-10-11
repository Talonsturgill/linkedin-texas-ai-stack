#!/usr/bin/env python3
"""Prepare small cover attachments and verify actual unsent Gmail RAW tool results."""
import argparse
import base64
import hashlib
import io
import json
import re
from email import policy
from email.parser import BytesParser
from email.utils import getaddresses
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs,urlsplit

from gmail_binding import private_path,raw_message_content

ROOT=Path(__file__).resolve().parents[1]


def delivered_link_target(href):
    """Recognize Gmail's HTTPS Google wrapper, retaining an exact single target."""
    try:
        url=urlsplit(href)
        if url.scheme=='https' and url.netloc.casefold() in ('google.com','www.google.com') and url.path=='/url':
            targets=parse_qs(url.query,keep_blank_values=True).get('q',[])
            if len(targets)==1:
                target=urlsplit(targets[0])
                if target.scheme in ('http','https') and target.netloc:return targets[0]
    except ValueError:pass
    return href


def write_private(path,value):
    path=private_path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');path.chmod(0o600)


class VisibleHTML(HTMLParser):
    def __init__(self,value):
        super().__init__(convert_charrefs=True);self.text=[];self.links=[];self.images=[];self.hidden=0
        self.feed(value)

    def handle_starttag(self,tag,attrs):
        if tag in ('head','style','script'):self.hidden+=1
        if self.hidden:return
        attrs=dict(attrs)
        if tag=='a' and attrs.get('href'):self.links.append(attrs['href'])
        if tag=='img' and attrs.get('src'):self.images.append(attrs['src'])
        if tag in ('p','div','pre','h1','h2','h3','li','tr','td','th','br'):self.text.append(' ')

    def handle_endtag(self,tag):
        if tag in ('head','style','script'):
            self.hidden=max(0,self.hidden-1);return
        if not self.hidden and tag in ('p','div','pre','h1','h2','h3','li','tr','td','th'):self.text.append(' ')

    def handle_data(self,data):
        if not self.hidden:self.text.append(data)

    def visible(self):return ' '.join(''.join(self.text).split())


def objects(value):
    if isinstance(value,dict):
        yield value
        for child in value.values():yield from objects(child)
    elif isinstance(value,list):
        for child in value:yield from objects(child)
    elif isinstance(value,str) and value.lstrip().startswith(('{','[')):
        try:parsed=json.loads(value)
        except (ValueError,TypeError):return
        yield from objects(parsed)


def raw_from_draft(candidate):
    if isinstance(candidate.get('raw'),str):return candidate['raw']
    message=candidate.get('message')
    if isinstance(message,dict) and isinstance(message.get('raw'),str):return message['raw']
    return None


def extract_result(records,*,draft_id=None,subject=None):
    calls={};matches=[]
    for record in records:
        message=record.get('message') or {};content=message.get('content') or []
        if not isinstance(content,list):continue
        for block in content:
            if not isinstance(block,dict):continue
            if block.get('type')=='tool_use':
                name=re.sub(r'[^a-z]','',str(block.get('name','')).lower())
                args=block.get('input') or {}
                if (name.endswith(('getdraft','getdraftemail'))
                        and args.get('messageFormat')=='RAW' and isinstance(args.get('draftId'),str)):
                    calls[block.get('id')]=args['draftId']
            elif block.get('type')=='tool_result' and not block.get('is_error'):
                requested=calls.get(block.get('tool_use_id'))
                if not requested or (draft_id and requested!=draft_id):continue
                candidates=list(objects(block.get('content')))
                if any(row.get('isError') is True for row in candidates):continue
                for candidate in candidates:
                    if candidate.get('id')!=requested:continue
                    raw=raw_from_draft(candidate)
                    if not raw:continue
                    actual_subject,_,_=raw_message_content(raw)
                    if subject and actual_subject!=subject:continue
                    matches.append(candidate);break
    if not matches:raise ValueError('No matching successful Get draft email RAW result in the current transcript')
    return matches[-1]


def prepare(payload,image_path=None):
    packet={'subject':payload['subject'],'bodyHtml':payload['payload']['body']['content']}
    if image_path is None:return packet,None
    from PIL import Image
    image=Image.open(image_path).convert('RGB');image.thumbnail((160,160))
    for quality in (55,45,35):
        buffer=io.BytesIO();image.save(buffer,format='JPEG',quality=quality,optimize=True)
        data=buffer.getvalue()
        if len(data)<=4096:break
    if len(data)>4096:raise ValueError('Preview exceeds the small attachment budget')
    attachment={'filename':'texas-stack-preview.jpg','mimeType':'image/jpeg',
                'content':base64.b64encode(data).decode()}
    packet={'subject':payload['subject'],'bodyHtml':payload['payload']['body']['content'],
            'attachments':[attachment]}
    proof={'filename':attachment['filename'],'mime_type':'image/jpeg','bytes':len(data),
           'sha256':hashlib.sha256(data).hexdigest(),'width':image.width,'height':image.height,
           'quality':quality}
    return packet,proof


def verify_delivery(payload,binding,readback,preview=None):
    checks={}
    checks['binding_verified']=binding.get('verified') is True
    raw=raw_from_draft(readback)
    if not raw:raise ValueError('Full RAW draft readback is required')
    message=BytesParser(policy=policy.default).parsebytes(
        base64.b64decode(raw+'='*(-len(raw)%4),altchars=b'-_',validate=True))
    labels=readback.get('labelIds',readback.get('label_ids',[]))
    if not labels and isinstance(readback.get('message'),dict):labels=readback['message'].get('labelIds',[])
    checks['draft_only']='DRAFT' in labels and 'SENT' not in labels
    checks['subject_matches']=str(message['Subject'])==payload['subject']
    recipient=binding.get('recipient','').casefold()
    actual_to=[address.casefold() for _,address in getaddresses(message.get_all('To',[]))]
    checks['recipient_matches']=actual_to==[recipient] and payload.get('to','').casefold()==recipient
    checks['no_extra_recipients']=not message.get_all('Cc',[]) and not message.get_all('Bcc',[])
    parts=[part for part in message.walk() if part.get_content_type()=='text/html'
           and not part.get_filename() and part.get_content_disposition()!='attachment']
    checks['one_full_html_body']=len(parts)==1
    actual=parts[0].get_content() if len(parts)==1 else ''
    expected=payload['payload']['body']['content']
    a=VisibleHTML(actual);e=VisibleHTML(expected)
    actual_links=[delivered_link_target(href) for href in a.links]
    checks['full_body_text_matches']=a.visible()==e.visible()
    checks['all_links_present']=all(url in actual_links for url in e.links)
    checks['pinned_cover_link_present']=any(
        re.fullmatch(r'https://raw\.githubusercontent\.com/Talonsturgill/linkedin-texas-ai-stack/[0-9a-f]{40}/out/post_image\.png',url)
        for url in actual_links)
    if preview:
        found=[]
        for part in message.walk():
            if part.get_filename()==preview['filename']:
                data=part.get_payload(decode=True) or b''
                found.append(part.get_content_type()==preview['mime_type']
                             and len(data)==preview['bytes']
                             and hashlib.sha256(data).hexdigest()==preview['sha256'])
        checks['preview_bytes_match']=found==[True]
    checks['mime_well_formed']=not message.defects
    return {'ok':all(checks.values()),'checks':checks,
            'exact_html_bytes_match':actual.replace('\r\n','\n').rstrip('\n')==expected.replace('\r\n','\n').rstrip('\n'),
            'inline_cover_retained':any(url in a.images for url in e.images),
            'delivery_image_mode':'attached_preview_and_full_cover_link' if preview else 'immutable_full_cover_link',
            'google_wrapped_link_count':sum(target!=href for href,target in zip(a.links,actual_links)),
            'markup_sanitized':actual.replace('\r\n','\n').rstrip('\n')!=expected.replace('\r\n','\n').rstrip('\n')}


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='mode',required=True)
    p=sub.add_parser('prepare');p.add_argument('--payload',required=True);p.add_argument('--image',help='Explicit optional preview attachment; default uses the immutable full-cover link');p.add_argument('--out',required=True)
    p=sub.add_parser('extract');p.add_argument('--transcript');selection=p.add_mutually_exclusive_group(required=True)
    selection.add_argument('--binding');selection.add_argument('--subject');p.add_argument('--out',required=True)
    p=sub.add_parser('verify')
    for arg in ('payload','binding','readback','out'):p.add_argument('--'+arg,required=True)
    p.add_argument('--preview',help='Require exact attachment bytes only when an attachment was explicitly requested')
    args=parser.parse_args()
    try:
        if args.mode=='prepare':
            payload=json.loads(private_path(args.payload).read_text())
            image=(ROOT/args.image).resolve() if args.image else None
            if image and not image.is_relative_to(ROOT):raise ValueError('Accepted artwork must stay inside this repository')
            packet,proof=prepare(payload,image);write_private(args.out,packet)
            if proof:
                proof_path=str(Path(args.out).with_suffix('.preview.json'));write_private(proof_path,proof)
            print(json.dumps({'prepared':True,'html_chars':len(packet['bodyHtml']),
                              'attachment_requested':proof is not None,'preview_bytes':proof['bytes'] if proof else 0}))
        elif args.mode=='extract':
            draft_id=None
            if args.binding:draft_id=json.loads(private_path(args.binding).read_text()).get('marker_draft_id')
            if args.binding and not draft_id:raise ValueError('Private binding lacks an explicit draft resource identifier')
            if args.transcript:paths=[Path(args.transcript)]
            else:
                project=Path.home()/'.claude/projects'/str(ROOT).replace('/','-')
                paths=sorted(project.glob('*.jsonl'),key=lambda p:p.stat().st_mtime,reverse=True)[:5]
            result=None
            for path in paths:
                with path.open() as handle:records=[json.loads(line) for line in handle if line.strip()]
                try:result=extract_result(records,draft_id=draft_id,subject=args.subject)
                except ValueError:continue
                break
            if result is None:raise ValueError('No matching actual RAW result; preserve the error and do not reconstruct it')
            write_private(args.out,result);print(json.dumps({'extracted':True,'actual_raw_tool_result':True,'private_output_written':True}))
        else:
            values={name:json.loads(private_path(getattr(args,name)).read_text()) for name in ('payload','binding','readback')}
            values['preview']=json.loads(private_path(args.preview).read_text()) if args.preview else None
            report=verify_delivery(**values);write_private(args.out,report);print(json.dumps(report))
            return 0 if report['ok'] else 1
    except (ValueError,KeyError,TypeError,OSError,UnicodeError):
        print(json.dumps({'ok':False,'error':'Private delivery preparation, extraction or verification failed; no identity or body was logged'}));return 1
    return 0


if __name__=='__main__':raise SystemExit(main())
