#!/usr/bin/env python3
"""Return the editorial date in Chicago, regardless of the cloud host's timezone."""
import argparse
import datetime as dt
import json
from zoneinfo import ZoneInfo


def context(at: dt.datetime | None = None) -> dict:
    instant=at or dt.datetime.now(dt.timezone.utc)
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError('The run instant must include a timezone')
    local=instant.astimezone(ZoneInfo('America/Chicago'))
    day=local.day
    suffix='th' if 11<=day%100<=13 else {1:'st',2:'nd',3:'rd'}.get(day%10,'th')
    return {'run_date':local.date().isoformat(),'timezone':'America/Chicago',
            'cover_date':f'{local:%B} {day}{suffix}, {local.year}',
            'checked_at_utc':instant.astimezone(dt.timezone.utc).isoformat()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--iso',action='store_true',help='Print only the Chicago ISO date')
    args=parser.parse_args();value=context()
    print(value['run_date'] if args.iso else json.dumps(value))


if __name__=='__main__':main()
