#!/usr/bin/env python3
"""Boot a started lab to the Practice menu (Classic Controller input).  usage: to_practice.py [remote]"""
import sys, time; sys.path.insert(0, '.')
from ctl import Lab; import flows
P = '/Volumes/SSD/larsen/Documents/Git/Super-Sluggers-Patch/lab/shots/'
l = Lab(); flows.boot_to_main_menu(l, remote=False, first_wait=60)
time.sleep(20)
flows.dpad(l, 'd', False); flows.press_a(l, False); time.sleep(15)
l.shot(P + 'pm.png'); print('practice menu')
