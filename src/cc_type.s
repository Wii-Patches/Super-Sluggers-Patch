# Hook at 0x8050B734 (game pad layer, after WPADProbe): `stb r0, 0x5c(r19)` stores the extension type
# that every other part of the game (menus, control pages, fielding, ...) tests.  Report a Classic
# Controller (2) as "no extension" (0) so the whole game treats it as the plain Wii Remote it already
# supports; the buttons/stick/motion come from our KPADRead hooks instead.
        cmpwi   r0, 2
        bne     keep
        li      r0, 0
keep:
        stb     r0, 0x5c(r19)
RETURN:
