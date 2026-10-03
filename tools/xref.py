import sys, struct
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from dol import Dol

def bl_callers(d, target):
    out = []
    for o, a, s, i in d.secs:
        if a < 0x80003000 or i > 6: continue
        for off in range(0, s, 4):
            w = struct.unpack('>I', d.data[o+off:o+off+4])[0]
            if (w >> 26) == 18 and (w & 1):          # bl
                li = w & 0x03FFFFFC
                if li & 0x02000000: li -= 0x04000000
                if (a + off + li) & 0xFFFFFFFF == target: out.append(a + off)
    return out
if __name__ == '__main__':
    d = Dol(sys.argv[1])
    for t in sys.argv[2:]:
        print(t, [hex(x) for x in bl_callers(d, int(t, 16))])
