"""m.py <keys...> : press each key (A, B, DOWN, PLUS, ZR, ...) with a pause, then screenshot to shots/m.png.
Use 'w<sec>' to wait."""
import sys, time; sys.path.insert(0, '.')
from ctl import Lab
l = Lab()
for a in sys.argv[1:]:
    if a[0] == 'w' and a[1:].isdigit(): time.sleep(int(a[1:]))
    else: l.cc(a, 0.8); time.sleep(4)
time.sleep(3); l.shot('/Volumes/SSD/larsen/Documents/Git/Super-Sluggers-Patch/lab/shots/m.png')
