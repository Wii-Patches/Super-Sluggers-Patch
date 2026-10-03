"""Closed-loop navigation: press a key, wait until the screen has really changed."""
import sys, time; sys.path.insert(0, '.')
from PIL import Image, ImageChops
SH = '/Volumes/SSD/larsen/Documents/Git/Super-Sluggers-Patch/lab/shots/'

def thumb(l, name):
    l.shot(SH + name)
    return Image.open(SH + name).convert('L').resize((64, 48))

def diff(a, b):
    d = ImageChops.difference(a, b)
    return sum(d.getdata()) / (64 * 48)

def step(l, key, hold=0.6, tries=6, wait=90, thr=8, settle=6, tag='nav'):
    """Press `key` until the picture changes by more than `thr`; returns True if it did."""
    for t in range(tries):
        before = thumb(l, tag + '_b.png')
        l.cc(key, hold)
        t0 = time.time()
        while time.time() - t0 < wait:
            time.sleep(4)
            now = thumb(l, tag + '_a.png')
            if diff(before, now) > thr:
                time.sleep(settle); return True
    return False
