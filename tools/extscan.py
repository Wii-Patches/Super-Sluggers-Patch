import sys, re
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from dol import Dol
from scan import insns
d = Dol(sys.argv[1]); off = sys.argv[2] if len(sys.argv) > 2 else '0x5c'
L = list(insns(d))
for k, ins in enumerate(L):
    m = re.match(r'lbz (r\d+), %s\((r\d+)\)' % off, f'{ins.mnemonic} {ins.op_str}')
    if not m: continue
    reg = m.group(1)
    for j in range(1, 8):
        if k + j >= len(L): break
        t = L[k + j]; s = f'{t.mnemonic} {t.op_str}'
        c = re.match(r'(cmpwi|cmplwi|cmpwi cr\d|cmplwi cr\d)\s+(?:cr\d, )?%s, (-?0x[0-9a-f]+|-?\d+)$' % reg, s)
        if c:
            print(f'{ins.address:08X} {ins.mnemonic} {ins.op_str:20} -> {t.address:08X} {s}')
            break
