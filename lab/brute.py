"""With the game waiting in the Throw state, replay candidate waveforms as the throw until the game reacts."""
import sys, time, struct, itertools; sys.path.insert(0, '.'); sys.path.insert(0, '../tools')
from ctl import Lab; import wait, sluggers as S
l = Lab(); R = (0, 0, 104)
def pack(c): return b''.join(struct.pack('>hhhh', max(-512, min(511, x)), max(-512, min(511, y)), max(-512, min(511, z)), 0) for x, y, z in c)
raw = l.read(0x80001B18, 0x120)
site = next(0x80001B18 + i for i in range(0, len(raw), 4) if (int.from_bytes(raw[i:i+4], 'big') >> 16) == 0x38C0 and (int.from_bytes(raw[i:i+4], 'big') & 0xffff) == 50 + len(S.DOWN))
print('N site', hex(site))
U = S.UP[:14]
cands = []
for perm in itertools.permutations(range(3)):
    for signs in itertools.product((1, -1), repeat=3):
        f = lambda s: tuple(signs[k] * s[perm[k]] for k in range(3))
        for rev in (False, True):
            seq = [f(s) for s in (U[::-1] if rev else U)]
            cands.append(('perm%s sgn%s rev%d' % (perm, signs, rev), seq + [R] * 4))
print(len(cands), 'candidates')
base = wait.score(l, 'throw')
for i, (name, c) in enumerate(cands):
    l.write(0x80002400 + 400, pack(c)); l.write(site, struct.pack('>I', 0x38C00000 | (50 + len(c))))
    l.cc('ZL', 0.8); time.sleep(4)
    sc = wait.score(l, 'throw')
    print(i, name, round(sc), flush=True)
    if sc > 20:
        print('REACTED', name); l.shot(wait.SH + 'brute_hit.png'); break
