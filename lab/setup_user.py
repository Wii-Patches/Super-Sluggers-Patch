#!/usr/bin/env python3
"""Create an isolated Dolphin user folder with pipe-driven pads (a resettable lab)."""
import os, sys, shutil, subprocess
args = [a for a in sys.argv[1:] if not a.startswith('--')]
root = os.path.abspath(args[0] if args else os.path.join(os.path.dirname(__file__), 'user'))
KEEP = '--keep' in sys.argv
if not KEEP: shutil.rmtree(root, ignore_errors=True)
for d in ('Config', 'Pipes', 'Wii', 'GameSettings', 'Load', 'Logs', 'ScreenShots', 'Dump'):
    os.makedirs(os.path.join(root, d), exist_ok=True)
for p in ('gc1', 'wm1', 'wm2'):
    if not os.path.exists(os.path.join(root, 'Pipes', p)): subprocess.check_call(['mkfifo', os.path.join(root, 'Pipes', p)])

open(os.path.join(root, 'Config', 'Dolphin.ini'), 'w').write("""[General]
GDBPort = 2345
[Core]
CPUCore = 1
SIDevice0 = 6
SIDevice1 = 0
SIDevice2 = 0
SIDevice3 = 0
WiiSDCardSyncFolder = False
WiimoteContinuousScanning = False
WiimoteEnableSpeaker = False
SyncOnSkipIdle = True
[Interface]
ConfirmStop = False
UsePanicHandlers = False
[Display]
Fullscreen = False
RenderWindowAutoSize = False
[DSP]
Backend = No Audio Output
[Input]
BackgroundInput = True
[Analytics]
Enabled = False
PermissionAsked = True
""")

# GameCube pad 1 <- pipe gc1
btn = lambda a, b: f"{a} = `Button {b}`"
gc = ["[GCPad1]", "Device = Pipe/0/gc1"] + [btn(a, b) for a, b in [
    ('Buttons/A', 'A'), ('Buttons/B', 'B'), ('Buttons/X', 'X'), ('Buttons/Y', 'Y'),
    ('Buttons/Z', 'Z'), ('Buttons/Start', 'START'),
    ('D-Pad/Up', 'D_UP'), ('D-Pad/Down', 'D_DOWN'), ('D-Pad/Left', 'D_LEFT'), ('D-Pad/Right', 'D_RIGHT')]]
for stick, name in (('Main Stick', 'MAIN'), ('C-Stick', 'C')):
    gc += [f"{stick}/Up = `Axis {name} Y +`", f"{stick}/Down = `Axis {name} Y -`",
           f"{stick}/Left = `Axis {name} X -`", f"{stick}/Right = `Axis {name} X +`"]
gc += ["Triggers/L = `Button L`", "Triggers/R = `Button R`", "Triggers/L-Analog = `Axis L +`", "Triggers/R-Analog = `Axis R +`"]
open(os.path.join(root, 'Config', 'GCPadNew.ini'), 'w').write("\n".join(gc) + "\n")

# Wiimote 1 <- pipe wm1 (extension chosen by -C override at run time)
def wm(n, pipe):
    L = [f"[Wiimote{n}]", "Source = 1", f"Device = Pipe/0/{pipe}"]
    L += [btn(f'Buttons/{a}', b) for a, b in [('A', 'A'), ('B', 'B'), ('1', 'X'), ('2', 'Y'), ('-', 'Z'), ('+', 'START'),
          ]]
    L += [btn(f'D-Pad/{a}', b) for a, b in [('Up', 'D_UP'), ('Down', 'D_DOWN'), ('Left', 'D_LEFT'), ('Right', 'D_RIGHT')]]
    L += ['Swing/Forward = `Button L`', 'Swing/Backward = `Button R`', 'Options/Sideways Wiimote = True',
          'Swing/Up = `Axis MAIN Y +`', 'Swing/Down = `Axis MAIN Y -`', 'Swing/Left = `Axis MAIN X -`', 'Swing/Right = `Axis MAIN X +`',
          'Shake/Z = `Axis R +`', 'Shake/Y = `Axis L +`']
    L += ['IR/Up = `Axis C Y +`', 'IR/Down = `Axis C Y -`', 'IR/Left = `Axis C X -`', 'IR/Right = `Axis C X +`']
    # Classic controller mapping (used when Extension = Classic)
    cc = [('A', 'A'), ('B', 'B'), ('X', 'X'), ('Y', 'Y'), ('ZL', 'Z'), ('+', 'START')]
    L += [btn(f'Classic/Buttons/{a}', b) for a, b in cc]
    L += [btn(f'Classic/D-Pad/{a}', b) for a, b in [('Up', 'D_UP'), ('Down', 'D_DOWN'), ('Left', 'D_LEFT'), ('Right', 'D_RIGHT')]]
    L += ['Classic/Buttons/ZR = `Axis C Y +`', 'Classic/Buttons/- = `Axis C X -`', 'Classic/Buttons/Home = `Axis C X +`']
    L += ["Classic/Left Stick/Up = `Axis MAIN Y +`", "Classic/Left Stick/Down = `Axis MAIN Y -`",
          "Classic/Left Stick/Left = `Axis MAIN X -`", "Classic/Left Stick/Right = `Axis MAIN X +`"]
    L += ["Classic/Triggers/L = `Axis L +`", "Classic/Triggers/R = `Axis R +`"]
    return L
open(os.path.join(root, 'Config', 'WiimoteNew.ini'), 'w').write("\n".join(wm(1, 'wm1')) + "\n")
open(os.path.join(root, 'Config', 'Hotkeys.ini'), 'w').write("""[Hotkeys]
Device = Quartz/0/Keyboard & Mouse
Load State/Load State Slot 1 = F1
Load State/Load State Slot 2 = F2
Save State/Save State Slot 1 = @(Shift+F1)
Save State/Save State Slot 2 = @(Shift+F2)
General/Take Screenshot = F9
""")
print('user dir ready:', root)
