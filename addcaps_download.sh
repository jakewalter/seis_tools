#!/bin/bash
#if [ "$#" -lt 1 ]; then
#    echo "Usage: $0 [year]"
#    exit 0
#fi

for g in waveforms/*.mseed; do rs2caps -I file://$g -d mysql://sysop:sysop@localhost/seiscomp3 -j ""; done;
