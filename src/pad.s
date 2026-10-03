# KPADRead (0x805FD3D8, once per call, after the newest sample's buttons are known).
#   r4 = extension type, r7 = remote buttons, r9 = Classic buttons, r27 = channel, r31 = KPAD status
# Folds a Classic Controller (extension 2) or the GameCube pad on the same port into the remote's
# button word, and records which gestures are held for the motion emulation (motion.s):
#   STATE + 16*channel: +0 held gestures, +4 position, +8 end, +12 pending gesture
# Face/menu buttons keep their remote meaning (A, B, 1, 2, +, -, Home) and the D-pad stays upright.
# L, R and friends are not remote buttons: they are the gestures (R swing, L shake, ...).
# scratch registers: r0, r3, r5, r6, r10, r11, r12 (all dead at this point of KPADRead)
        .macro  MAP cls, rem
        andi.   r0, r9, \cls
        beq     1f
        ori     r7, r7, \rem
1:
        .endm
        .macro  GMAP cls, rem
        andis.  r0, r3, \cls
        beq     1f
        ori     r7, r7, \rem
1:
        .endm
        .macro  GEST cls, gesture
        andi.   r0, r9, \cls
        beq     1f
        ori     r10, r10, \gesture
1:
        .endm
        li      r10, 0
        cmpwi   r4, 2
        bne     gamecube
        MAP     0x0010, 0x0800          # A      -> A
        MAP     0x0040, 0x0400          # B      -> B
        MAP     0x0008, 0x0100          # X      -> 2
        MAP     0x0020, 0x0200          # Y      -> 1
        MAP     0x0400, 0x0010          # +      -> +
        MAP     0x1000, 0x1000          # -      -> -
        MAP     0x0800, 0x8000          # HOME   -> Home
        MAP     0x0001, 0x0008          # up     -> up
        MAP     0x4000, 0x0004          # down   -> down
        MAP     0x0002, 0x0001          # left   -> left
        MAP     0x8000, 0x0002          # right  -> right
        GEST    0x0200, SWING           # R      -> swing
        GEST    0x2000, SHAKE           # L      -> shake
        GEST    0x0004, PITCH_UP        # ZR     -> pitch up
        GEST    0x0080, PITCH_DOWN      # ZL     -> pitch down
        b       state

# GameCube pad: the SI hardware answers for port N once its channel is polled.  The game never runs
# the PAD library, so switch the polling on here (idempotent) and read the result registers directly.
#   INBUFH: 31 error, 23 always set, 28..24 Start Y X B A, 22..16 L R Z up down right left, 15..8 stick X, 7..0 stick Y
#   INBUFL: C-stick X, C-stick Y, L, R analog
gamecube:
        mulli   r11, r27, 12
        lis     r12, 0xCD00
        ori     r12, r12, 0x6400
        add     r12, r12, r11           # SIC<n>OUTBUF
        lis     r3, 0x0040
        ori     r3, r3, 0x0300          # command: analog mode 3, no rumble
        lwz     r0, 0(r12)
        cmpw    r0, r3
        beq     1f
        stw     r3, 0(r12)
1:      lis     r6, 0xCD00
        ori     r6, r6, 0x6430          # SIPOLL: channel enable bits 7..4
        li      r0, 0x80
        srw     r0, r0, r27
        lwz     r5, 0(r6)
        and.    r11, r5, r0
        bne     2f
        or      r5, r5, r0
        stw     r5, 0(r6)
2:      lwz     r3, 4(r12)
        lwz     r5, 8(r12)
        andis.  r0, r3, 0x8000
        bne     state                   # error / no pad
        andis.  r0, r3, 0x0080
        beq     state                   # no answer yet
        GMAP    0x0100, 0x0800          # A      -> A
        GMAP    0x0200, 0x0400          # B      -> B
        GMAP    0x0400, 0x0100          # X      -> 2
        GMAP    0x0800, 0x0200          # Y      -> 1
        GMAP    0x1000, 0x0010          # Start  -> +
        GMAP    0x0008, 0x0008          # up     -> up
        GMAP    0x0004, 0x0004          # down   -> down
        GMAP    0x0001, 0x0001          # left   -> left
        GMAP    0x0002, 0x0002          # right  -> right
        rlwinm  r0, r3, 24, 24, 31      # stick X
        cmpwi   r0, 168
        blt     3f
        ori     r7, r7, 0x0002
3:      cmpwi   r0, 88
        bgt     4f
        ori     r7, r7, 0x0001
4:      rlwinm  r0, r3, 0, 24, 31       # stick Y
        cmpwi   r0, 168
        blt     5f
        ori     r7, r7, 0x0008
5:      cmpwi   r0, 88
        bgt     6f
        ori     r7, r7, 0x0004
6:      andis.  r0, r3, 0x0020          # R -> swing
        beq     7f
        ori     r10, r10, SWING
7:      andis.  r0, r3, 0x0040          # L -> shake
        beq     8f
        ori     r10, r10, SHAKE
8:      andis.  r0, r3, 0x0010          # Z -> pitch up
        beq     9f
        ori     r10, r10, PITCH_UP
9:      rlwinm  r0, r5, 16, 24, 31      # C-stick Y: down -> pitch down
        cmpwi   r0, 88
        bgt     10f
        ori     r10, r10, PITCH_DOWN
10:     oris    r10, r10, 0x8000        # a pad is answering on this channel

state:  lis     r3, STATE@h
        ori     r3, r3, STATE@l
        slwi    r11, r27, 4
        add     r3, r3, r11
        lwz     r0, 0(r3)
        stw     r10, 0(r3)
        andc    r0, r10, r0             # gestures that just went down
        andi.   r5, r0, SWING
        beq     11f
        li      r5, 1
        stw     r5, 12(r3)
11:     andi.   r5, r0, PITCH_UP
        beq     12f
        li      r5, 3
        stw     r5, 12(r3)
12:     andi.   r5, r0, PITCH_DOWN
        beq     13f
        li      r5, 4
        stw     r5, 12(r3)
13:
        andi.   r0, r7, 0x9fff
RETURN:
