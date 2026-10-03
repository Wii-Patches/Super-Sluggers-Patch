import sys, struct
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from dol import Dol
from capstone import Cs, CS_ARCH_PPC, CS_MODE_32, CS_MODE_BIG_ENDIAN, CS_MODE_PS

md = Cs(CS_ARCH_PPC, CS_MODE_32 | CS_MODE_BIG_ENDIAN | CS_MODE_PS)
md.skipdata = True

def dis(d, start, end):
    code = d.read(start, end - start)
    for i in md.disasm(code, start):
        print(f'{i.address:08X}  {i.bytes.hex()}  {i.mnemonic:8} {i.op_str}')

if __name__ == '__main__':
    d = Dol(sys.argv[1])
    dis(d, int(sys.argv[2], 16), int(sys.argv[3], 16))
