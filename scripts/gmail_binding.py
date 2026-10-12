#!/usr/bin/env python3
"""Load a private profile binding and verify its unsent mailbox challenge without logging identity."""
import argparse
import base64
import binascii
import datetime as dt
from email import policy
from email.parser import BytesParser
from email.utils import getaddresses
import json
import os
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ENV='TEXAS_STACK_GMAIL_BINDING'


def load_binding(environ):
    value=json.loads(environ.get(ENV,'{}'))
    if value.get('schema_version')!=1 or value.get('profile_provider')!='authenticated_gmail_profile':
        raise ValueError('Missing authenticated profile binding in the routine environment')
    if not re.fullmatch(r'[^\s<>@]+@[^\s<>@]+\.[^\s<>@]+',value.get('recipient','')):
        raise ValueError('Private recipient binding is invalid')
    if not re.fullmatch(r'[a-f0-9]{32}',value.get('marker','')) or not value.get('marker_subject'):
        raise ValueError('Private mailbox challenge is missing')
    for kind in ('message','thread','draft'):
        identifier=value.get('marker_'+kind+'_id')
        if identifier is not None and (not isinstance(identifier,str)
                or not re.fullmatch(r'[A-Za-z0-9_-]{1,512}',identifier)):
            raise ValueError('Private challenge '+kind+' identifier is invalid')
    if value.get('marker_thread_id') and not value.get('marker_message_id'):
        raise ValueError('Private thread challenge requires the bound message identifier')
    if value.get('marker_draft_id') and not value.get('marker_message_id'):
        raise ValueError('Private draft challenge requires the bound message identifier')
    dt.datetime.fromisoformat(value['profile_verified_at_utc'].replace('Z','+00:00'))
    return value


def dictionaries(value):
    if isinstance(value,dict):
        yield value
        for child in value.values():yield from dictionaries(child)
    elif isinstance(value,list):
        for child in value:yield from dictionaries(child)


def strings(value):
    if isinstance(value,str):yield value
    elif isinstance(value,dict):
        for child in value.values():yield from strings(child)
    elif isinstance(value,list):
        for child in value:yield from strings(child)


def mime_body_text(part):
    """Read inline Gmail API text parts without decoding unrelated response fields."""
    if not isinstance(part,dict):return
    body=part.get('body') or {}
    data=body.get('data') if isinstance(body,dict) else None
    if (isinstance(data,str) and not part.get('filename')
            and str(part.get('mimeType','text/plain')).startswith('text/')):
        try:
            yield base64.b64decode(data+'='*(-len(data)%4),altchars=b'-_',validate=True).decode('utf-8')
        except (ValueError,binascii.Error,UnicodeDecodeError):pass
    for child in part.get('parts',[]):yield from mime_body_text(child)


def challenge_candidates(readback,draft_id):
    for candidate in dictionaries(readback):
        if not draft_id:
            yield candidate
        elif any(candidate.get(key)==draft_id for key in ('id','draft_id','draftId')):
            yield candidate
            # Gmail REST nests the message; Claude's connector returns a flat draft.
            if isinstance(candidate.get('message'),dict):yield candidate['message']


def raw_message_content(raw):
    """Decode a real draft RAW result, excluding attachment and header-only markers."""
    if not isinstance(raw,str):return None,[],[]
    try:
        data=base64.b64decode(raw+'='*(-len(raw)%4),altchars=b'-_',validate=True)
        message=BytesParser(policy=policy.default).parsebytes(data)
        if message.defects:return None,[],[]
        text=[]
        for part in message.walk():
            if (part.get_content_maintype()=='text' and not part.get_filename()
                    and part.get_content_disposition()!='attachment'):
                content=part.get_content()
                if isinstance(content,str):text.append(content)
        recipients=[address.casefold() for _,address in getaddresses(message.get_all('To',[]))]
        return str(message['Subject']) if message['Subject'] is not None else None,text,recipients
    except (ValueError,binascii.Error,UnicodeError,LookupError):return None,[],[]


def verify(binding,readback):
    # A random challenge issued only as a draft in the authenticated mailbox proves
    # cross-connector access. No sender or recipient field is used as identity evidence.
    for candidate in challenge_candidates(readback,binding.get('marker_draft_id')):
        expected_id=binding.get('marker_message_id')
        if expected_id and not any(candidate.get(key)==expected_id
                for key in ('id','message_id','messageId')):
            continue
        subject=candidate.get('subject')
        payload=candidate.get('payload') or {}
        if isinstance(payload,dict):
            for header in payload.get('headers',[]):
                if header.get('name','').lower()=='subject':subject=header.get('value')
        body_keys=('body','body_html','body_text','bodyHtml','bodyText',
                   'htmlBody','plaintextBody','html','text')
        text=[s for key in body_keys for s in strings(candidate.get(key))]
        text+=list(mime_body_text(payload))
        if 'raw' in candidate:
            subject,text,recipients=raw_message_content(candidate['raw'])
            # Identity still comes from the authenticated profile plus challenge.
            # This equality permits the already-verified address to be reused as
            # a routing value from Gmail's own metadata, without printing the env.
            if binding.get('recipient') and recipients!=[binding['recipient'].casefold()]:continue
        if subject!=binding['marker_subject']:continue
        labels=[]
        for key,value in candidate.items():
            if key.lower().replace('_','') in ('labels','labelids') and isinstance(value,list):
                labels.extend(strings(value))
        if any(binding['marker'] in s for s in text):
            if 'DRAFT' in labels and 'SENT' not in labels:
                return True
    return False


def private_path(value):
    path=(ROOT/value).resolve()
    if not path.is_relative_to(ROOT) or not path.is_relative_to((ROOT/'.local').resolve()):
        raise ValueError('Private binding output must stay under ignored .local')
    return path


def recipient_from_binding(path):
    value=json.loads(private_path(path).read_text())
    if value.get('schema_version')!=1 or value.get('verified') is not True:
        raise ValueError('Mailbox binding has not passed the challenge readback')
    if not re.fullmatch(r'[^\s<>@]+@[^\s<>@]+\.[^\s<>@]+',value.get('recipient','')):
        raise ValueError('Verified private binding contains an invalid recipient')
    return value['recipient']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',required=True)
    parser.add_argument('--readback',help='Ignored JSON containing the connector full readback')
    args=parser.parse_args()
    try:
        value=load_binding(os.environ)
        verified=False
        if args.readback:
            verified=verify(value,json.loads(private_path(args.readback).read_text()))
            if not verified:raise ValueError('Mailbox challenge readback failed; do not write a draft')
        value['verified']=verified
        destination=private_path(args.out);destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_text(json.dumps(value,indent=2)+'\n');destination.chmod(0o600)
        print(json.dumps({'binding_loaded':True,'mailbox_challenge_verified':verified,'private_output_written':True}))
    except (ValueError,KeyError,TypeError) as error:
        print(json.dumps({'binding_loaded':False,'mailbox_challenge_verified':False,'error':str(error)}))
        raise SystemExit(1)


if __name__=='__main__':main()
