#!/usr/bin/env python3
"""Lab daemon: owns one Dolphin run, its GDB connection and its input pipes.
Talk to it with lab/ctl.py (JSON lines over 127.0.0.1:47731)."""
import json, os, re, socket, subprocess, sys, threading, time
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
def _watch():
    rc = proc.wait(); print('dolphin exited, returncode', rc, time.strftime('%H:%M:%S'), flush=True)
threading.Thread(target=_watch, daemon=True).start()
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
    if op == 'pad':           # input pipes need no GDB access: usable while a watch holds the lock
        for line in req['lines']:
            os.write(pipe(req['pipe']), (line + '\n').encode())
        return {}
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
                    if w.get('kCGWindowOwnerPID') == proc.pid and 'RMBE' in (w.get('kCGWindowName') or '')]
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
        if op == 'watch':
            # hardware read/write watchpoints: report the PCs that hit within `secs`
            kind = {'x': 0, 'w': 2, 'r': 3, 'a': 4}[req.get('kind', 'r')]
            g.halt(); hits = []
            ranges = req['ranges']
            reps = []
            for a, n in ranges:
                reps.append(g.cmd('Z%d,%x,%x' % (kind, a, n)))
            t0 = time.time(); g.cont()
            while time.time() - t0 < req['secs'] and len(hits) < req.get('max', 40):
                g._fill(0.5)
                stops = [p for p in g._packets() if p.startswith('T') or p.startswith('S')]
                for _ in stops:
                    g.running = False
                    m = re.search(r'40:([0-9a-f]{8})', _)
                    hits.append('0x' + m.group(1) if m else _)
                    g.cont()
            g.halt()
            for a, n in ranges:
                g.cmd('z%d,%x,%x' % (kind, a, n))
            g.cont()
            return {'hits': hits, 'replies': reps}
        if op == 'cont':
            g.running = False; g.cont(); return {}
        if op == 'alive':
            return {'alive': proc.poll() is None}
        if op == 'quit':
            proc.kill(); os._exit(0)
    return {'error': 'bad op'}

srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(('127.0.0.1', 47731)); srv.listen(8)
def serve(c):
    try:
        for line in c.makefile():
            try: resp = handle(json.loads(line))
            except Exception as e: resp = {'error': repr(e)}
            c.sendall((json.dumps(resp) + '\n').encode())
    except OSError:
        pass
    finally:
        c.close()
while True:
    c, _ = srv.accept()
    threading.Thread(target=serve, args=(c,), daemon=True).start()
