import json, socket, sys, time
class Lab:
    def __init__(self):
        self.c = socket.create_connection(('127.0.0.1', 47731), timeout=60); self.f = self.c.makefile()
    def call(self, **r):
        self.c.sendall((json.dumps(r) + '\n').encode()); resp = json.loads(self.f.readline())
        if 'error' in resp: raise RuntimeError(resp['error'])
        return resp
    def read(self, addr, n): return bytes.fromhex(self.call(op='read', addr=addr, len=n)['hex'])
    def u32(self, a): return int.from_bytes(self.read(a, 4), 'big')
    def write(self, addr, data): self.call(op='write', addr=addr, hex=bytes(data).hex())
    def pad(self, pipe, *lines): self.call(op='pad', pipe=pipe, lines=list(lines))
    def press(self, pipe, b, secs=0.15):
        self.pad(pipe, f'PRESS {b}'); time.sleep(secs); self.pad(pipe, f'RELEASE {b}'); time.sleep(0.1)
    def shot(self, path, tries=6):
        for i in range(tries):
            try: return self.call(op='shot', path=path)
            except RuntimeError:
                if i == tries - 1: return self.shot_local(path)
                time.sleep(1.5)
    def shot_local(self, path):
        """Capture without the daemon (it only sees on-screen windows; this also finds occluded ones)."""
        import subprocess, Quartz
        pids = [int(l.split()[0]) for l in subprocess.check_output(
            "ps -axo pid,command | grep 'Sluggers-Patch/lab/user' | grep -v grep", shell=True, text=True).splitlines()]
        for w in Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionAll, 0):
            if w.get('kCGWindowOwnerPID') in pids and 'RMBE' in (w.get('kCGWindowName') or ''):
                subprocess.check_call(['screencapture', '-x', '-o', '-l', str(w['kCGWindowNumber']), path]); return {}
        raise RuntimeError('no window')

    def point(self, x, y, pipe='wm1'):
        """Move the Wii Remote pointer; x,y in 0..1 of the screen (y down)."""
        self.pad(pipe, f'SET C {x:.3f} {1 - y:.3f}'); time.sleep(0.4)
    def click(self, x, y, wait=3, pipe='wm1'):
        self.point(x, y, pipe); self.press(pipe, 'A', 0.25); time.sleep(wait)

# ---- Classic Controller / GameCube helpers (pipe wm1 in Classic mode; pipe gc1 for the GC pad)
CC = {
    'A': ('PRESS A', 'RELEASE A'), 'B': ('PRESS B', 'RELEASE B'), 'X': ('PRESS X', 'RELEASE X'),
    'Y': ('PRESS Y', 'RELEASE Y'), 'ZL': ('PRESS Z', 'RELEASE Z'), 'PLUS': ('PRESS START', 'RELEASE START'),
    'UP': ('PRESS D_UP', 'RELEASE D_UP'), 'DOWN': ('PRESS D_DOWN', 'RELEASE D_DOWN'),
    'LEFT': ('PRESS D_LEFT', 'RELEASE D_LEFT'), 'RIGHT': ('PRESS D_RIGHT', 'RELEASE D_RIGHT'),
    'L': ('SET L 1.0', 'SET L 0.0'), 'R': ('SET R 1.0', 'SET R 0.0'),
    'ZR': ('SET C 0.5 1.0', 'SET C 0.5 0.5'), 'MINUS': ('SET C 0.0 0.5', 'SET C 0.5 0.5'),
    'HOME': ('SET C 1.0 0.5', 'SET C 0.5 0.5'),
}
GC = {k: ('PRESS ' + k, 'RELEASE ' + k) for k in ('A', 'B', 'X', 'Y', 'Z', 'START', 'L', 'R')}
GC.update({'UP': ('PRESS D_UP', 'RELEASE D_UP'), 'DOWN': ('PRESS D_DOWN', 'RELEASE D_DOWN'),
           'LEFT': ('PRESS D_LEFT', 'RELEASE D_LEFT'), 'RIGHT': ('PRESS D_RIGHT', 'RELEASE D_RIGHT')})

def _tap(self, table, pipe, names, secs):
    names = names.split('+') if isinstance(names, str) else names
    self.pad(pipe, *[table[n][0] for n in names]); time.sleep(secs)
    self.pad(pipe, *[table[n][1] for n in names]); time.sleep(0.15)
def cc(self, names, secs=0.2): _tap(self, CC, 'wm1', names, secs)
def gc(self, names, secs=0.2): _tap(self, GC, 'gc1', names, secs)
def stick(self, x, y, pipe='wm1', which='MAIN'): self.pad(pipe, f'SET {which} {(x + 1) / 2:.3f} {(y + 1) / 2:.3f}')
Lab.cc, Lab.gc, Lab.stick = cc, gc, stick

def init_pads(self):
    for pipe in ('wm1', 'gc1'):
        try:
            self.pad(pipe, 'SET MAIN 0.5 0.5', 'SET C 0.5 0.5', 'SET L 0.0', 'SET R 0.0')
        except Exception: pass
Lab.init_pads = init_pads

F_KEYS = {1: 122, 2: 120, 3: 99, 4: 118, 5: 96}
def save_state(self, slot=1): self.call(op='key', code=F_KEYS[slot], shift=True)
def load_state(self, slot=1): self.call(op='key', code=F_KEYS[slot], shift=False)
Lab.save_state, Lab.load_state = save_state, load_state

import struct as _st
RING, CTRL, TABLE = 0x80002800, 0x80002F00, 0x80002400
def ring_reset(self): self.write(CTRL + 0xC, bytes(4))
def ring_read(self):
    """Return the newest-last list of logged raw samples (x, y, z, buttons, ext, err)."""
    idx = self.u32(CTRL + 0xC)
    raw = self.read(RING, 64 * 16)
    n = min(idx, 64)
    out = []
    for i in range(idx - n, idx):
        e = raw[(i & 63) * 16:(i & 63) * 16 + 16]
        x, y, z, b = _st.unpack('>hhhH', e[:8]); out.append((x, y, z, b, e[8], e[9]))
    return out
def inject(self, samples):
    """Replay raw accel (x,y,z) triples into channel 0, one per KPAD sample."""
    data = b''.join(_st.pack('>hhhh', x, y, z, 0) for x, y, z in samples)
    self.write(TABLE, data)
    self.write(CTRL + 4, _st.pack('>II', 0, len(samples)))
    self.write(CTRL, _st.pack('>I', 1))
Lab.ring_reset, Lab.ring_read, Lab.inject = ring_reset, ring_read, inject
