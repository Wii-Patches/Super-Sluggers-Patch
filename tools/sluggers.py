"""Feature definitions for Mario Super Sluggers (USA, RMBE01), built from src/*.s."""
import os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asm
from layout import CAVE_BASE, CAVE_LIMIT
from ops import Feature, Hook, Patch

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src')
NOP = 0x60000000

def source(name):
    return open(os.path.join(SRC, name)).read()

class Cave:
    """Bump allocator for trampolines in the injected section."""
    def __init__(self, base=CAVE_BASE):
        self.next = base
    def alloc(self, nwords):
        a = self.next
        self.next += 4 * nwords
        assert self.next <= CAVE_LIMIT, 'cave full'
        return a

def hook(dol, cave, site, src, note='', consts=None, syms=None):
    """Assemble `src` (a routine that ends by falling off the end or `b RETURN`) into a trampoline
    that must itself execute the displaced instruction when the source says so."""
    orig = struct.unpack('>I', dol.read(site, 4))[0]
    text = source(src) if src.endswith('.s') else src
    # assemble once to learn the size, then again at the final address
    n = len(asm.words(asm.assemble(text, 0x80001820, consts=consts, syms=syms))) + 1
    tramp = cave.alloc(n)
    words = asm.words(asm.assemble(text, tramp, consts=consts, syms=syms)) + [NOP]
    return Hook(site, orig, words, tramp, note)

CTRL, TABLE, RING = 0x80002F00, 0x80002400, 0x80002800

def dbg_motion(dol):
    """DEV ONLY: log raw accelerometer samples / replay waveforms from the lab."""
    from ops import Blob
    cave = Cave(0x80002000)
    h = hook(dol, cave, 0x805FD4C8, 'dbg_motion.s', 'DEV: log raw accel / inject waveform',
             consts=dict(CTRL=CTRL, TABLE=TABLE, RING=RING))
    return Feature('dbg', 'Motion debug', 'RMBE01', [h, Blob(0x80002400, bytes(0xC00), 'zeroed tables/ring/control')])

REST = (0, 0, 104)
WAVES, STATE = 0x80002400, 0x80002F00
SWING = [(-512, 366, 404)] + [(-512, 510, 508)] * 5 + [(-512, 366, 404), (-512, 180, 252)] + [REST] * 3 + \
        [(511, -190, -48), (511, -374, -200), (511, -190, -48)] + [REST] * 6
SHAKE = ([(511, 0, 104)] * 3 + [(-512, 0, 104)] * 3) * 2
UP = [(18, -4, 100), (138, -32, 508), (172, -38, 508), (68, -16, 508), (-226, 50, 508), (-512, 168, 508),
      (-512, 232, 508), (-512, 256, 508), (-512, 232, 508), (-512, 152, 508), (-79, 16, 68), (511, -160, -216),
      (511, -350, -264), (511, -164, -112)] + [REST] * 4
DOWN = [(114, -26, 60)] * 4 + [REST] * 4   # placeholder until captured

def waves():
    """Concatenate the gesture waveforms; returns (blob, assembler constants)."""
    seq, consts, n = [], dict(SWING=1, SHAKE=2, PITCH_UP=4, PITCH_DOWN=8, WAVES=WAVES, STATE=STATE), 0
    for name, w in (('SWING', SWING), ('SHAKE', SHAKE), ('UP', UP), ('DOWN', DOWN)):
        consts[name + '_AT'], consts[name + '_N'] = n, len(w)
        seq += w; n += len(w)
    return b''.join(struct.pack('>hhhh', x, y, z, 0) for x, y, z in seq), consts

def controllers(dol):
    """Classic Controller + GameCube pad: buttons, extension override and motion emulation."""
    from ops import Blob
    cave = Cave()
    blob, consts = waves()
    ops = [
        hook(dol, cave, 0x805FD3D8, 'pad.s', 'KPADRead: Classic / GameCube buttons -> remote bits, gestures', consts=consts),
        hook(dol, cave, 0x805FCD00, 'cc_dpad.s', 'KPADRead: Classic left stick -> D-pad'),
        hook(dol, cave, 0x8050B734, 'cc_type.s', 'pad layer: Classic Controller reported as plain remote'),
        hook(dol, cave, 0x805FD4C8, 'motion.s', 'KPADRead: gestures replay swing/shake waveforms', consts=consts),
        Blob(WAVES, blob, 'gesture waveforms'),
        Blob(STATE, bytes(64), 'gesture state'),
    ]
    return Feature('ctl', 'Classic / GameCube controller', 'RMBE01', ops)
