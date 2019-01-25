#!/bin/bash

############################################################################
# Copyright (C) 2017 by gempa GmbH                                         #
#                                                                          #
# All Rights Reserved.                                                     #
#                                                                          #
# NOTICE: All information contained herein is, and remains                 #
# the property of gempa GmbH and its suppliers, if any. The intellectual   #
# and technical concepts contained herein are proprietary to gempa GmbH    #
# and its suppliers.                                                       #
# Dissemination of this information or reproduction of this material       #
# is strictly forbidden unless prior written permission is obtained        #
# from gempa GmbH.                                                         #
#                                                                          #
# Author: Dirk Roessler                                                    #
# Email: roessler@gempa.de                                                 #
############################################################################

# XML offline playback based on waveforms


#####################################
# the basic script:

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 [sorted mseed-volume]"
    exit 0
fi

set -x; 
seiscomp stop
DBFLAG="mysql://sysop:sysop@localhost/seiscomp3"
VERBOSITY="-v"

#echo "2017,08,23,18,00,00 2017,08,23,18,06,00 * * * *" | capstool -H 10.27.192.71:18002 -o tempOK.mseed

#scautopick --ep --playback -I file://$1 -d $DBFLAG > picks.xml 
#scautoloc --ep picks.xml -d $DBFLAG $VERBOSITY > origins.xml
#scanloc --ep picks.xml -d localhost $VERBOSITY > origins2.xml
#scamp --ep origins2.xml -I file://$1 -d $DBFLAG $VERBOSITY > amps.xml
#scmag --ep amps.xml -d $DBFLAG $VERBOSITY > mags.xml
#scevent --ep mags.xml -d $DBFLAG $VERBOSITY > events.xml

scxmldump -fI -o inventory.xml -d $DBFLAG $VERBOSITY
scxmldump -fC -o config.xml -d $DBFLAG $VERBOSITY


scautopick --ep --playback -I file://$1 --inventory-db inventory.xml --config-db config.xml > picks.xml 
scanloc --ep picks.xml --inventory-db inventory.xml --config-db config.xml > origins.xml
scamp --ep origins.xml -I file://$1 --inventory-db inventory.xml --config-db config.xml > amps.xml
scmag --ep amps.xml --inventory-db inventory.xml --config-db config.xml > mags.xml
scevent --ep mags.xml --inventory-db inventory.xml --config-db config.xml > events.xml



scdb -i events.xml -d $DBFLAG $VERBOSITY
seiscomp start
scdispatch -i events.xml -d $DBFLAG $VERBOSITY

#####################################
# view results:

# seiscomp start scmaster spread
# scolv --debug

#####################################
# with messaging:

# seiscomp start spread scmaster scautoloc scanloc scamp scmag scevent
# scdispatch -H <host> -O update -i <file>.xml

#####################################
# dump configurations:

#scxmldump -fI -o inventory.xml -d $DBFLAG $VERBOSITY
#scxmldump -fC -o config.xml -d $DBFLAG $VERBOSITY

#####################################
# Advanced tuning:

# SEISCOMP_LOCAL_CONFIG=.
# bindings2cfg --key-dir /home/dirk/seiscomp3/etc/key -o config.xml
# seiscomp exec scolv --offline
