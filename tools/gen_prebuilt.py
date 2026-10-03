#!/usr/bin/env python3
"""Regenerate tools/prebuilt/ctl_RMBE01.json from src/ (needs the retail main.dol).

    SLUGGERS_DOL=/path/to/main.dol  python3 tools/gen_prebuilt.py

Defaults to work/main.orig.dol.  The JSON is what the patcher ships and reads;
end users do not need any game files here.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dol import Dol
from features import PREBUILT, dump
import sluggers

REGION = 'RMBE01'


def main():
    path = os.environ.get('SLUGGERS_DOL') or os.path.join(HERE, '..', 'work', 'main.orig.dol')
    if not os.path.exists(path):
        sys.exit('set SLUGGERS_DOL=<path to the retail main.dol>')
    dol = Dol(path)
    f = sluggers.controllers(dol)
    os.makedirs(PREBUILT, exist_ok=True)
    out = os.path.join(PREBUILT, 'ctl_%s.json' % REGION)
    with open(out, 'w') as fh:
        json.dump(dump(f), fh, indent=1)
        fh.write('\n')
    print('ctl %s  %d ops -> %s' % (REGION, len(f.ops), os.path.relpath(out)))


if __name__ == '__main__':
    main()
