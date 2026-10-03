"""Apply a feature's writes to a running game over the GDB link (no rebuild, works after loading a save state)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from dol import Dol
import sluggers

def apply(lab, *names):
    dol = Dol(os.path.join(ROOT, 'work/main.orig.dol'))
    n = 0
    for name in names:
        feat = getattr(sluggers, name)(dol)
        for addr, data in feat.writes():
            lab.write(addr, data); n += len(data)
    return n
