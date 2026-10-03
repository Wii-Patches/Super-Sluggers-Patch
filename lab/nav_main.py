#!/usr/bin/env python3
"""Closed-loop boot to the pitching practice, wound up (ZR) and waiting for the throw."""
import sys, time; sys.path.insert(0, '.')
from ctl import Lab; import nav
l = Lab(); S = nav.SH
def log(m): print(time.strftime('%H:%M:%S'), m, flush=True)
log('title ' + str(nav.step(l, 'A+B', tag='a1', settle=10)))
log('right ' + str(nav.step(l, 'RIGHT', tag='a2', thr=4, settle=3)))
log('file ' + str(nav.step(l, 'A', tag='a3', settle=6)))
log('start ' + str(nav.step(l, 'A', tag='a4', settle=10)))
time.sleep(100); l.shot(S + 'a5.png'); log('main menu?')
