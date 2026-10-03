# Technical notes

## Why earlier Classic Controller hacks failed

The game asks the Wii for the extension type in several places and acts on it.
Here the poll at `0x8050B5A4` stores the WPADProbe result in the per-channel
buffer (`stb r0,0x5c(r19)` at `0x8050B734`); `cc_type.s` reports a Classic
Controller (2) as "none" (0) there, so the game keeps treating the pad as a
plain remote.

## Input path

KPADRead is statically linked at `0x805FCE10`. Its status struct is
`0x80784CD8 + channel*0x538`; `+0x5C` is the extension type and `+0..+8` /
`+0x60..+0x68` are remote / Classic hold, pressed, released.

| Hook site | Source | Purpose |
| --- | --- | --- |
| `0x805FD3D8` | `src/pad.s` | once per KPADRead: fold Classic or GameCube buttons into the remote bits, note held gestures |
| `0x805FCD00` | `src/cc_dpad.s` | Classic left stick to D-pad bits (upright menus) |
| `0x8050B734` | `src/cc_type.s` | hide the Classic extension type |
| `0x805FD4C8` | `src/motion.s` | per sample: replay a swing/shake/pitch accelerometer waveform |

Waveforms (`tools/sluggers.py`) were captured from real remote motion in
Dolphin. Gesture state lives at `0x80002F00`, waveforms at `0x80002400`.

## GameCube pad

The game links the SI library but never runs the PAD library, so `pad.s`
switches SI polling on itself (`SIC<n>OUTBUF = 0x00400300`, `SIPOLL` enable bit)
and reads `SIC<n>INBUFH/L`.

## Hooks and the injected section

Trampolines sit at `0x80001820-0x80003000`, which the game never touches. The
ops (`Hook`, `Patch`, `Blob`) in `tools/ops.py` render the same feature as a
patched DOL, Gecko codes or Riivolution XML.

## Tools

- `tools/dev.py` patches `work/main.orig.dol` and rebuilds `work/dev.wbfs`
- `lab/` is a Dolphin remote-control harness (pipe input, GDB memory access)
