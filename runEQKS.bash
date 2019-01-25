#!/bin/bash

# run EQKS on Nicoya dataset to get catalogPS 
source ~/.bashrc
cd ~/niclocate
db2EQKS_v1.pl /data3/mendenhall/nicoyaclean/nicclean EQKS_1 2012-001 2012-290
db2EQKS_v1.pl /data3/mendenhall/nicoyaclean/nicclean EQKS_2 2012-290 2012-365
db2EQKS_v1.pl /data3/mendenhall/nicoyaclean/temp1/temp1 EQKS_3 2012-305 2012-337
cp EQKS_1 EQKS
simul2000_hypo3big
locPS2catalog.bash summary2 catalogPS_1
cp EQKS_2 EQKS
simul2000_hypo3big
locPS2catalog.bash summary2 catalogPS_2
cp EQKS_3 EQKS
simul2000_hypo3big
locPS2catalog.bash summary2 catalogPS_3
cat catalogPS_1 catalogPS_2 catalogPS_3 > catalogPS
cp catalogPS ~/Nicoya3/
cd ~/Nicoya3
build_bettercatalog.bash
