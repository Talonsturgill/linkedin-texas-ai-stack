#!/usr/bin/env python3
"""Plan exact type before ImageGen; output geometry, never artwork or aesthetic scores."""
import argparse
import json
from pathlib import Path
from compose_cover import font_pair
from art_layout import headline_layout


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--headline',required=True)
    p.add_argument('--out',required=True)
    a=p.parse_args()
    layout=headline_layout(a.headline,font_pair()[0])
    destination=Path(a.out);destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(layout,indent=2)+'\n')
    print(json.dumps({'layout':str(destination),'lines':layout['lines'],
                      'subject_zone':layout['subject_zone'],'headline_top':layout['headline_top']}))

if __name__=='__main__':main()
