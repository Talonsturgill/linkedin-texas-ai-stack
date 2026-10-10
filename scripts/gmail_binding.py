#!/usr/bin/env python3
"""Load a private profile binding and verify its unsent mailbox challenge without logging identity."""
import argparse
import datetime as dt
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


def verify(binding,readback):
    # A random challenge issued only as a draft in the authenticated mailbox proves
    # cross-connector access. No sender or recipient field is used as identity evidence.
    for candidate in dictionaries(readback):
        subject=candidate.get('subject')
        payload=candidate.get('payload') or {}
        if isinstance(payload,dict):
            for header in payload.get('headers',[]):
                if header.get('name','').lower()=='subject':subject=header.get('value')
        if subject!=binding['marker_subject']:continue
        text=list(strings(candidate));labels=[]
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
