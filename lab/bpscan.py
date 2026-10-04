import sys,time; sys.path.insert(0,'.')
from ctl import Lab
l=Lab()
sites=[0x801ca9a0,0x801cb490,0x8024b2a0,0x80516500,0x80516650,0x80516490,0x805165e0]
R=[[a,4] for a in sites]
def tally(h): 
    from collections import Counter; return dict(Counter(h['hits']))
print('idle  ',tally(l.call(op='watch',kind='x',ranges=R,secs=8,max=80)))
print('idle2 ',tally(l.call(op='watch',kind='x',ranges=R,secs=8,max=80)))
