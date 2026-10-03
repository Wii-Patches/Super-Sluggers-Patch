#!/usr/bin/env python3
"""From a started lab to the pitching practice, wound up and waiting for the throw."""
import sys, time; sys.path.insert(0, '.')
from ctl import Lab; import flows
l = Lab(); flows.boot_to_main_menu(l, remote=False, first_wait=60); time.sleep(40)
from PIL import Image
def crop_sum(p):
    im = Image.open(p).convert('L').crop((260, 170, 380, 270)); return sum(im.getdata()) / (120 * 100)
P = '/Volumes/SSD/larsen/Documents/Git/Super-Sluggers-Patch/lab/shots/tt_menu.png'
l.shot(P); base = crop_sum(P)
for _ in range(4):                                                    # select Practice (verify by pixels)
    l.cc('DOWN', 0.6); time.sleep(3); l.shot(P)
    if abs(crop_sum(P) - base) > 12: break
l.cc('A', 0.5); time.sleep(15)
for _ in range(3): l.cc('A', 0.5); time.sleep(6)                     # Pitching, lesson 1, tutorial
l.cc('PLUS', 0.5); time.sleep(20); l.cc('A', 0.5); time.sleep(6)     # skip demo
l.cc('ZR', 0.5); time.sleep(3); print('wound up')
