#!/usr/bin/env python3
"""Start the lab detached (own session) on a game image and wait until it answers.
usage: lab/start.py <image> [metal]   -> stops any earlier lab first"""
import os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
subprocess.call([os.path.join(HERE, 'stop.sh')]); time.sleep(2)
ext = next((a.split('=')[1] for a in sys.argv[2:] if a.startswith('ext=')), 'None')
ini = os.path.join(HERE, 'user', 'Config', 'WiimoteNew.ini')
lines = [l for l in open(ini).read().split('\n') if not l.startswith('Extension')]
if ext == 'Classic':   # the remote's own buttons must not echo the Classic inputs
    lines = [l for l in lines if not l.startswith(('Buttons/', 'D-Pad/'))]
lines.insert(lines.index('[Wiimote1]') + 1, 'Extension = ' + ext)
open(ini, 'w').write('\n'.join(lines))
speed = next((a.split('=')[1] for a in sys.argv[2:] if a.startswith('speed=')), None)
env = dict(os.environ)
if 'metal' in sys.argv[2:]: env['VIDEO'] = 'Metal'
if speed: env['LAB_ARGS'] = '-C Dolphin.Core.EmulationSpeed=' + speed
subprocess.Popen([sys.executable, os.path.join(HERE, 'labd.py'), os.path.abspath(sys.argv[1])],
                 stdout=open(os.path.join(HERE, 'labd.log'), 'w'), stderr=subprocess.STDOUT,
                 stdin=subprocess.DEVNULL, start_new_session=True, env=env)
sys.path.insert(0, HERE)
from ctl import Lab
t0 = time.time()
while time.time() - t0 < 240:
    try:
        l = Lab(); l.read(0x80000000, 4); l.init_pads(); print('lab up'); break
    except Exception: time.sleep(1)
else:
    sys.exit('lab did not come up')
