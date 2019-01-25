#!/bin/bash
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 [year]"
    exit 0
fi

for f in $1/*/*seed; do rs2caps -I file://$f -d mysql://sysop:sysop@localhost/seiscomp3 -j ""; done;
