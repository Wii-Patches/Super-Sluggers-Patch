# DEV ONLY. Hook at 0x805FD4C8. Logs channel 0's raw accelerometer samples that differ from rest
# (0, 0, 104) into RING, newest last, no wrapping, up to 112 entries.  CTRL+0xC = entries logged.
        cmpwi   r27, 0
        bne     done
        lha     r8, 2(r19)
        lha     r9, 4(r19)
        lha     r10, 6(r19)
        cmpwi   r8, 0
        bne     log
        cmpwi   r9, 0
        bne     log
        cmpwi   r10, 104
        beq     done
log:
        lis     r3, CTRL@h
        ori     r3, r3, CTRL@l
        lwz     r5, 0xC(r3)
        cmpwi   r5, 112
        bge     done
        slwi    r6, r5, 4
        lis     r7, RING@h
        ori     r7, r7, RING@l
        add     r7, r7, r6
        sth     r8, 0(r7)
        sth     r9, 2(r7)
        sth     r10, 4(r7)
        addi    r5, r5, 1
        stw     r5, 0xC(r3)
done:
        mr      r3, r31
RETURN:
