import sys,time,threading; sys.path.insert(0,'.')
from ctl import Lab
from collections import Counter
l=Lab()
print('sanity', dict(Counter(l.call(op='watch',kind='x',ranges=[[0x80001820,4]],secs=3,max=5)['hits'])))
sites=[0x801ca9a0,0x801cb490,0x8024b2a0,0x80516500,0x80516650,0x80516490,0x805165e0,0x8050c034,0x8050c0b8]
R=[[a,4] for a in sites]
def press():
    time.sleep(2); l2=Lab(); l2.pad('wm1','SET MAIN 0.5 0.0'); time.sleep(1); l2.pad('wm1','SET MAIN 0.5 0.5')
threading.Thread(target=press).start()
print('swing ', dict(Counter(l.call(op='watch',kind='x',ranges=R,secs=15,max=200)['hits'])))
