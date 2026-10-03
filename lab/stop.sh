#!/bin/bash
# stop only this project's lab processes (daemon + the Dolphin using the lab user dir)
for p in $(ps -axo pid,command | grep -E "lab/labd.py|Sluggers-Patch/lab/user" | grep -v grep | awk '{print $1}'); do kill -9 $p 2>/dev/null; done
