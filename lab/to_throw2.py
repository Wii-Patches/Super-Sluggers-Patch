#!/usr/bin/env python3
"""Scene-driven boot to the pitching practice: windup done, waiting for the throw."""
import sys, time; sys.path.insert(0, '.')
from ctl import Lab; import wait
l = Lab(); did_right = False; t_start = time.time()
def log(m): print(time.strftime('%H:%M:%S'), m, flush=True)
order = ['demo', 'startmenu', 'throw', 'pullup', 'tutorial', 'lesson', 'main_prac', 'main', 'practice', 'files', 'title']
while time.time() - t_start < 2400:
    sc = {s: wait.score(l, s) for s in order}
    hit = wait.hit(sc)
    log('%s  %s' % (hit, ' '.join('%s=%.0f' % (k, v) for k, v in sc.items())))
    if hit == 'throw': log('READY'); break
    elif hit == 'pullup': l.cc('ZR', 2.5)
    elif hit == 'demo': l.cc('PLUS', 2.5)
    elif hit == 'startmenu': l.cc('A', 2.5)
    elif hit == 'tutorial': l.cc('A', 2.5)
    elif hit == 'lesson': l.cc('A', 2.5)
    elif hit == 'main_prac': l.cc('A', 2.5)
    elif hit == 'main': l.cc('DOWN', 2.5)
    elif hit == 'practice': l.cc('A', 2.5)
    elif hit == 'files':
        l.cc('A', 2.5)
    elif hit == 'title': l.cc('A+B', 2.5)
    time.sleep(15)
