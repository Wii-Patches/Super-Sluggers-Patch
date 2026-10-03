import sys, struct
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from dol import Dol
from capstone import Cs, CS_ARCH_PPC, CS_MODE_32, CS_MODE_BIG_ENDIAN, CS_MODE_PS
md = Cs(CS_ARCH_PPC, CS_MODE_32 | CS_MODE_BIG_ENDIAN | CS_MODE_PS); md.skipdata = True

def insns(d):
    for o, a, s, i in d.secs:
        if i > 6: continue
        for ins in md.disasm(bytes(d.data[o:o+s]), a):
            yield ins
if __name__ == '__main__':
    import re
    d = Dol(sys.argv[1]); pat = re.compile(sys.argv[2])
    for ins in insns(d):
        t = f'{ins.mnemonic} {ins.op_str}'
        if pat.search(t): print(f'{ins.address:08X}  {t}')
