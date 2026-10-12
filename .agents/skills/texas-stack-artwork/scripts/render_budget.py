"""Persist production render reservations across concepts, source edits and failures."""
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import subprocess
from pathlib import Path

LIMIT=6
ROOT=Path(__file__).resolve().parents[4]


def production_ledger():
    branch=subprocess.check_output(['git','symbolic-ref','--short','HEAD'],cwd=ROOT,text=True).strip()
    key=hashlib.sha256(branch.encode()).hexdigest()[:16]
    return ROOT/'.local'/f'art-budget-{key}.json',branch


@contextlib.contextmanager
def locked(path):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.with_suffix('.lock').open('a') as guard:
        fcntl.flock(guard,fcntl.LOCK_EX)
        yield path


def read(path,branch):
    if not path.exists():return {'schema_version':1,'branch':branch,'limit':LIMIT,'attempts':[]}
    value=json.loads(path.read_text())
    if (value.get('schema_version')!=1 or value.get('branch')!=branch
            or value.get('limit')!=LIMIT or not isinstance(value.get('attempts'),list)
            or len(value['attempts'])>LIMIT):
        raise ValueError('Invalid render budget; preserve it and stop')
    for i,row in enumerate(value['attempts'],1):
        if not isinstance(row,dict) or row.get('number')!=i:
            raise ValueError('Invalid render reservations; preserve them and stop')
    return value


def write(path,value):
    temporary=path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value,indent=2)+'\n');temporary.chmod(0o600)
    temporary.replace(path)


def reservation(value,number):
    if type(number) is not int or not 1<=number<=len(value['attempts']):
        raise ValueError('Invalid render reservation number')
    return value['attempts'][number-1]


def reserve(path,branch,spec_hash,renderer_hash,*,layout_hash=None,visual_spec_hash=None):
    with locked(path) as path:
        value=read(path,branch)
        if len(value['attempts'])>=LIMIT:raise ValueError('Six render reservations used; no further production image')
        number=len(value['attempts'])+1
        value['attempts'].append({'number':number,'status':'started',
            'started_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
            'spec_sha256':spec_hash,'renderer_sha256':renderer_hash,
            'layout_sha256':layout_hash,'visual_spec_sha256':visual_spec_hash})
        write(path,value)
        return number


def finish(path,branch,number,*,base_hash=None,error_type=None):
    with locked(path) as path:
        value=read(path,branch);row=reservation(value,number)
        if row['status']!='started':raise ValueError('Render reservation already finalized')
        row['status']='saved' if base_hash else 'failed'
        if base_hash:row['base_sha256']=base_hash
        if error_type:row['error_type']=error_type
        write(path,value)
        return value


def rebind(path,branch,number,*,base_hash,spec_hash,renderer_hash,layout_hash,visual_spec_hash):
    """Rebind nonvisual evidence metadata only; this function never draws pixels."""
    with locked(path) as path:
        value=read(path,branch);row=reservation(value,number)
        if (row.get('status')!='saved' or row.get('base_sha256')!=base_hash
                or row.get('renderer_sha256')!=renderer_hash or row.get('layout_sha256')!=layout_hash
                or not visual_spec_hash or row.get('visual_spec_sha256')!=visual_spec_hash):
            raise ValueError('Evidence rebind requires unchanged pixels, layout, renderer and visual specification')
        row.setdefault('rebind_history',[]).append({'previous_spec_sha256':row['spec_sha256'],
            'spec_sha256':spec_hash,'at_utc':dt.datetime.now(dt.timezone.utc).isoformat()})
        row['spec_sha256']=spec_hash;write(path,value)
        return value
