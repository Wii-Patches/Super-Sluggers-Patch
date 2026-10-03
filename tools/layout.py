"""Where the hook trampolines live in the injected low-memory section.

0x80001800-0x80003000 is the Wii's boot-time scratch area; Mario Super Sluggers
never touches it (checked at runtime: it stays zero through the menus).  The
first 0x20 bytes are skipped (the word at 0x80001800 is rewritten by the OS).
"""
CAVE_BASE = 0x80001820
CAVE_LIMIT = 0x80003000
