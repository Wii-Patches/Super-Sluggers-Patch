#!/usr/bin/env python3
"""Lab daemon: owns one Dolphin run, its GDB connection and its input pipes.
Talk to it with lab/ctl.py (JSON lines over 127.0.0.1:47731)."""
import json, os, socket, subprocess, sys, threading, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gdb import Gdb

game = sys.argv[1]
env = dict(os.environ)
args = ['/Applications/Dolphin.app/Contents/MacOS/Dolphin', '-u', os.path.join(HERE, 'user'), '-b', '-e', game,
        '-v', os.environ.get('VIDEO', 'Null')] + os.environ.get('LAB_ARGS', '').split() + sys.argv[2:]
log = open(os.path.join(HERE, 'dolphin.log'), 'w')
proc = subprocess.Popen(args, stdout=log, stderr=log)
print('dolphin pid', proc.pid, flush=True)
g = Gdb(); g.cont()
print('gdb attached', flush=True)

pipes = {}
def pipe(name):
    if name not in pipes:
        pipes[name] = os.open(os.path.join(HERE, 'user', 'Pipes', name), os.O_WRONLY | os.O_NONBLOCK)
    return pipes[name]

lock = threading.Lock()
def handle(req):
    op = req['op']
    with lock:
        if op == 'read':
            return {'hex': g.read(req['addr'], req['len']).hex()}
        if op == 'write':
            g.write(req['addr'], bytes.fromhex(req['hex'])); return {}
        if op == 'pad':
            for line in req['lines']:
                os.write(pipe(req['pipe']), (line + '\n').encode())
            return {}
        if op == 'shot':
            import Quartz
            wins = [w for w in Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionAll, 0)
                    if w.get('kCGWindowOwnerPID') == proc.pid and w.get('kCGWindowIsOnscreen') and 'RMBE' in (w.get('kCGWindowName') or '')]
            if not wins: return {'error': 'no window'}
            wid = max(wins, key=lambda w: w['kCGWindowBounds']['Width'])['kCGWindowNumber']
            subprocess.check_call(['screencapture', '-x', '-o', '-l', str(wid), req['path']])
            return {}
        if op == 'key':
            import Quartz
            code = req['code']; flags = Quartz.kCGEventFlagMaskShift if req.get('shift') else 0
            for down in (True, False):
                ev = Quartz.CGEventCreateKeyboardEvent(None, code, down)
                Quartz.CGEventSetFlags(ev, flags)
                Quartz.CGEventPostToPid(proc.pid, ev); time.sleep(0.08)
            return {}
        if op == 'alive':
            return {'alive': proc.poll() is None}
        if op == 'quit':
            proc.kill(); os._exit(0)
    return {'error': 'bad op'}

srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(('127.0.0.1', 47731)); srv.listen(4)
while True:
    c, _ = srv.accept()
    try:
        for line in c.makefile():
            try: resp = handle(json.loads(line))
            except Exception as e: resp = {'error': repr(e)}
            c.sendall((json.dumps(resp) + '\n').encode())
    finally:
        c.close()
