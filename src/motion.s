# KPADRead (0x805FD4C8, per raw sample; r19 = raw sample slot, r27 = channel).
# The game is played by shaking and swinging the remote.  While a pad gesture is pending or held
# (see pad.s) the matching accelerometer waveform from WAVES (8 bytes per sample: s16 x, y, z, pad)
# replaces the real sample, so the game's own gesture code fires.  Gesture ids: 1 swing, 2 shake,
# 3 pitch up, 4 pitch down.  STATE + 16*channel: +0 held, +4 position, +8 end, +12 pending id.
        cmpwi   r27, 3
        bgt     done
        slwi    r10, r27, 4
        lis     r3, STATE@h
        ori     r3, r3, STATE@l
        add     r10, r10, r3
        lwz     r5, 4(r10)
        lwz     r6, 8(r10)
        cmpw    r5, r6
        blt     play
        lwz     r8, 12(r10)
        cmpwi   r8, 0
        bne     pick
        lwz     r8, 0(r10)
        andi.   r0, r8, SHAKE
        beq     done
        li      r8, 2
pick:   li      r0, 0
        stw     r0, 12(r10)
        li      r5, SWING_AT
        li      r6, SWING_AT + SWING_N
        cmpwi   r8, 1
        beq     start
        li      r5, SHAKE_AT
        li      r6, SHAKE_AT + SHAKE_N
        cmpwi   r8, 2
        beq     start
        li      r5, UP_AT
        li      r6, UP_AT + UP_N
        cmpwi   r8, 3
        beq     start
        li      r5, DOWN_AT
        li      r6, DOWN_AT + DOWN_N
start:  stw     r6, 8(r10)
play:   slwi    r7, r5, 3
        lis     r3, WAVES@h
        ori     r3, r3, WAVES@l
        add     r7, r7, r3
        lhz     r8, 0(r7)
        lhz     r9, 2(r7)
        lhz     r0, 4(r7)
        sth     r8, 2(r19)
        sth     r9, 4(r19)
        sth     r0, 6(r19)
        addi    r5, r5, 1
        stw     r5, 4(r10)
done:
        mr      r3, r31
RETURN:
