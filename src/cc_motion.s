# KPADRead (0x805FD4C8, per raw sample; r19 = raw sample slot, r31 = KPAD status, r27 = channel).
# The game plays by shaking and swinging the remote.  For a Classic Controller the buttons below
# replay the matching accelerometer waveform into the sample, so the game's own gesture code fires:
#   R -> swing (bat / throw)   L -> shake (dash)   ZR -> pitch up   ZL -> pitch down
# Control: STATE + 16*channel = { +4 position, +8 end } into WAVES (8 bytes per sample: s16 x,y,z,0)
        lbz     r3, 0x28(r19)
        cmpwi   r3, 2
        bne     done
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
        lwz     r8, 0x64(r31)           # Classic buttons pressed this sample
        lwz     r9, 0x60(r31)           # Classic buttons held
        li      r5, 0
        li      r6, 0
        andi.   r0, r8, 0x0200          # R
        beq     1f
        li      r5, SWING_AT
        li      r6, SWING_AT + SWING_N
        b       start
1:      andi.   r0, r9, 0x2000          # L (held)
        beq     2f
        li      r5, SHAKE_AT
        li      r6, SHAKE_AT + SHAKE_N
        b       start
2:      andi.   r0, r8, 0x0004          # ZR
        beq     3f
        li      r5, UP_AT
        li      r6, UP_AT + UP_N
        b       start
3:      andi.   r0, r8, 0x0080          # ZL
        beq     done
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
