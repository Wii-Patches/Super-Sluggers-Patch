#!/usr/bin/env python3
"""Dev loop: patch work/main.orig.dol -> work/extracted/sys/main.dol, rebuild work/dev.wbfs.
usage: tools/dev.py [feature ...]   (no feature = clean build)"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from dol import Dol
from ops import apply_static
import sluggers

dol = Dol(os.path.join(ROOT, 'work/main.orig.dol'))
feats = [getattr(sluggers, n)(dol) for n in sys.argv[1:]]
if feats:
    apply_static(dol, feats)
dol.save(os.path.join(ROOT, 'work/extracted/sys/main.dol'))
subprocess.check_call(['wit', 'copy', os.path.join(ROOT, 'work/extracted'), os.path.join(ROOT, 'work/dev.wbfs'),
                       '--wbfs', '--overwrite', '-q'])
print('built dev.wbfs with', sys.argv[1:] or 'no patches')
