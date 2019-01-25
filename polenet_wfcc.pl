#!/usr/bin/perl -w

# temp? is each component merged using gsac already

`sac << END
r temp?
rmean
taper
transfer from evalresp to vel freqlimits .01 .02 40 50
hp c 5
w append i
quit
END`;
`sliding_wfcc_fix_v5 -f YT.HOWD.BHZ.SAC.vel.hp.stack -s tempZi -b -0.2 -a 0.8 -B 200 -A 2595201 -S 0.025 -O 0 -t 0.05 -F1 -o YT.HOWD.BHZ.SAC.vel.hp.detect2.sac`;
`sliding_wfcc_fix_v5 -f YT.HOWD.BHE.SAC.vel.hp.stack -s tempEi -b -0.2 -a 0.8 -B 200 -A 2595201 -S 0.025 -O 0 -t 0.05 -F1 -o YT.HOWD.BHE.SAC.vel.hp.detect2.sac`;
`sliding_wfcc_fix_v5 -f YT.HOWD.BHN.SAC.vel.hp.stack -s tempNi -b -0.2 -a 0.8 -B 200 -A 2595201 -S 0.025 -O 0 -t 0.05 -F1 -o YT.HOWD.BHN.SAC.vel.hp.detect2.sac`;
`ls *detect2.sac > templist`;
`XmengStackShift templist 3 1 tempstack3.sac > 9times_howd.dat`;
