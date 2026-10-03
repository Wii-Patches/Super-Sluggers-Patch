"""Scripted menu flows (time based; each ends with a screenshot you can eyeball)."""
import time

def boot_to_main_menu(l, remote=True, first_wait=75):
    """From a fresh boot to the Main Menu, with the Wii Remote (A/B/D-pad) or Classic (L+R / L)."""
    time.sleep(first_wait)
    for _ in range(3):
        press_ab(l, remote); time.sleep(3)
    time.sleep(45)
    press_a(l, remote)               # "Start game" popup on the file card
    time.sleep(55)

def press_a(l, remote=True):
    l.press('wm1', 'A', 0.3) if remote else l.cc('A', 0.3)
def press_b(l, remote=True):
    l.press('wm1', 'B', 0.3) if remote else l.cc('B', 0.3)
def press_ab(l, remote=True):
    if remote:
        l.pad('wm1', 'PRESS A', 'PRESS B'); time.sleep(0.3); l.pad('wm1', 'RELEASE A', 'RELEASE B'); time.sleep(0.2)
    else:
        l.cc('A+B', 0.3)
def dpad(l, d, remote=True):
    # Dolphin's sideways remote sends rotated bits; pick the button whose KPAD bit is the menu direction
    name = {'u': 'D_LEFT', 'd': 'D_RIGHT', 'l': 'D_DOWN', 'r': 'D_UP'}[d]
    if remote:
        l.pad('wm1', 'PRESS ' + name); time.sleep(0.35); l.pad('wm1', 'RELEASE ' + name); time.sleep(0.9)
    else:
        n = {'u': 'UP', 'd': 'DOWN', 'l': 'LEFT', 'r': 'RIGHT'}[d]
        l.cc(n, 0.35); time.sleep(0.9)
