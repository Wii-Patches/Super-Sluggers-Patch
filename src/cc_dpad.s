# Vague Rant / user hint, unmodified except comment syntax
# To be inserted at 805FCD00
# read_kpad_stick
# Inserted at 805FCD00 (Classic left stick BCTRL)
  bctrl
  cmpwi r15, 0x1
  bne- RETURN

# magic
  bl GRAB
MAGIC:
    THRESHOLD:  .float 0.5
    ZERO:       .float 0.0
GRAB:
  mflr r3

  lfs f2, THRESHOLD-MAGIC(r3)
  lfs f3, ZERO-MAGIC(r3)
  lwz r4, -0x60(r30)    # currently held
  lwz r5, -0x5C(r30)    # pressed this frame
  lwz r6, -0x58(r30)    # released this frame

  lfs f1, 0x0C(r30)     # left stick x axis
  li r8, 0x1
  bl STICK_EMULATION

  lfs f1, 0x10(r30)     # left stick y axis
  li r8, 0x4
  bl STICK_EMULATION
  stw r4, -0x60(r30)
  stw r5, -0x5C(r30)
  stw r6, -0x58(r30)
  b RETURN

STICK_EMULATION:
  fabs f0, f1
  fcmpo cr0, f0, f2     # is stick more than halfway?
  bltlr-

  fcmpo cr0, f1, f3     # positive or negative direction?
  blt- AXIS_SKIP
  slwi r8, r8, 0x1      # left->right / down->up

    AXIS_SKIP:
      and. r0, r6, r8       # was this button already being held?
      bne- NOT_NEW
      or r5, r5, r8         # add to buttons newly pressed

    NOT_NEW:
      or r4, r4, r8         # add to buttons held
      andc. r6, r6, r8      # remove from buttons released

  blr

RETURN: