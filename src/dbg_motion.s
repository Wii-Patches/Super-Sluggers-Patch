# DEV ONLY. Hook at 0x805FD4C8 (KPADRead second loop, `mr r3,r31` displaced).
#   r19 = raw WPAD sample slot (+0 buttons, +2/+4/+6 s16 accel X/Y/Z, +0x28 ext type, +0x29 err)
#   r27 = channel.  Control block CTRL: +0 mode(0 idle,1 inject) +4 step +8 length +0xC ring index
#   Injection table TABLE: 8 bytes/step: s16 x,y,z,pad.   Ring RING: 16 bytes/entry: x,y,z,buttons,chan,ext
        cmpwi   r27, 0
        bne     done
        lis     r3, CTRL@h
        ori     r3, r3, CTRL@l
        lwz     r4, 0(r3)
        cmpwi   r4, 0
        beq     log
        lwz     r5, 4(r3)
        slwi    r6, r5, 3
        lis     r7, TABLE@h
        ori     r7, r7, TABLE@l
        add     r7, r7, r6
        lhz     r8, 0(r7)
        lhz     r9, 2(r7)
        lhz     r10, 4(r7)
        sth     r8, 2(r19)
        sth     r9, 4(r19)
        sth     r10, 6(r19)
        addi    r5, r5, 1
        stw     r5, 4(r3)
        lwz     r6, 8(r3)
        cmpw    r5, r6
        blt     log
        li      r4, 0
        stw     r4, 0(r3)
log:
        lwz     r5, 0xC(r3)
        andi.   r6, r5, 0x3F
        slwi    r6, r6, 4
        lis     r7, RING@h
        ori     r7, r7, RING@l
        add     r7, r7, r6
        lhz     r8, 2(r19)
        sth     r8, 0(r7)
        lhz     r8, 4(r19)
        sth     r8, 2(r7)
        lhz     r8, 6(r19)
        sth     r8, 4(r7)
        lhz     r8, 0(r19)
        sth     r8, 6(r7)
        lbz     r8, 0x28(r19)
        stb     r8, 8(r7)
        lbz     r8, 0x29(r19)
        stb     r8, 9(r7)
        addi    r5, r5, 1
        stw     r5, 0xC(r3)
done:
        mr      r3, r31
RETURN:
