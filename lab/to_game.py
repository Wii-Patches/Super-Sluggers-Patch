#!/usr/bin/env python3
"""Boot the lab image (already started) to the exhibition tutorial/demo with a Classic Controller."""
import sys, time; sys.path.insert(0, '.')
from ctl import Lab; import flows
P = '/Volumes/SSD/larsen/Documents/Git/Sluggers-Patch/lab/shots/'
l = Lab(); flows.boot_to_main_menu(l, remote=False, first_wait=60); time.sleep(30)
flows.press_a(l, False); time.sleep(40)
l.shot(P + 'tg.png'); print('at game')
