# KPADRead (0x805FD3D8): fold the Classic Controller buttons into the remote button word.
#   r4 = extension type, r7 = remote buttons, r9 = Classic buttons
# Face/menu buttons keep their remote meaning (A, B, 1, 2, +, -, Home) and the D-pad stays upright.
# L, R, ZL and ZR are not remote buttons: they drive the motion emulation (cc_motion.s).
        cmpwi   r4, 2
        bne     done
        .macro  MAP cls, rem
        andi.   r0, r9, \cls
        beq     1f
        ori     r7, r7, \rem
1:
        .endm
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
done:
        andi.   r0, r7, 0x9fff
RETURN:
