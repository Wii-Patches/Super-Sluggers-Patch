#!/bin/bash
# usage: lab/run.sh <game dir or iso> [extra -C overrides...]   (Wiimote 1 extension: WM_EXT=Classic|None|Nunchuk)
HERE="$(cd "$(dirname "$0")" && pwd)"
GAME="$1"; shift
EXT="${WM_EXT:-None}"
exec /Applications/Dolphin.app/Contents/MacOS/Dolphin -u "$HERE/user" -b -e "$GAME" -v "${VIDEO:-Null}" \
  -C "Dolphin.Core.GDBPort=2345" "$@" >"$HERE/dolphin.log" 2>&1
