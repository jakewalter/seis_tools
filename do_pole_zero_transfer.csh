#!/bin/csh

# yet another way to do the transfer using the pole and zero file
# generated using lupei's code
# directory from: /mnt/data/scsn/Tremor
#
# tutorial
# http://geophysics.eas.gatech.edu/zpeng/Teaching/EAS8803_S08/misc/SeisII_L10.pdf
# user name: geophysics
# passwd: tectosphere

if ( $#argv == 4 ) then
	set switcher = $4
	set chan = $3
	set stn = $2
	set net = $1
else if ( $#argv == 3 ) then
	set switcher = 0
	set chan = "BH"
	set stn = $2
	set net = $1
else if ( $#argv == 2 ) then
	set switcher = 0
	set chan = "BH"
	set stn = $1
	set net = "YT"
else
	set switcher = 0
	set stn = "HOWD"
	set net = "YT"
endif


set SEED_dir = "."
if (`expr $switcher` > 0) then
	set chan1 = `printf "$chan\n" | gawk '{print $1"Z"}'`
	set chan2 = `printf "$chan\n" | gawk '{print $1"1"}'`
	set chan3 = `printf "$chan\n" | gawk '{print $1"2"}'`
else
	set chan1 = `printf "$chan\n" | gawk '{print $1"Z"}'`
	set chan2 = `printf "$chan\n" | gawk '{print $1"N"}'`
	set chan3 = `printf "$chan\n" | gawk '{print $1"E"}'`
endif


set PZ_BHZ = `ls SACPZ.${net}.${stn}.*${chan1} | tail -1`
set PZ_BHN = `ls SACPZ.${net}.${stn}.*${chan2} | tail -1`
set PZ_BHE = `ls SACPZ.${net}.${stn}.*${chan3} | tail -1`

printf "$PZ_BHZ $PZ_BHN $PZ_BHE\n"

# get the time range for cutting

set wf_b = `saclst b e f ${net}.{$stn}.*${chan1}*.SAC ${net}.{$stn}.*${chan2}*.SAC ${net}.{$stn}.*${chan3}*.SAC | gawk '{print $2,$3}' | minmax -I1 -C | gawk '{print $2}'`



set wf_e = `saclst b e f ${net}.{$stn}.*${chan1}*.SAC ${net}.{$stn}.*${chan2}*.SAC ${net}.{$stn}.*${chan3}*.SAC | gawk '{print $2,$3}' | minmax -I1 -C | gawk '{print $3}'`

printf "$wf_b $wf_e\n"

# set ff1 = 0.02
# set ff2 = 0.05
# set ff3 = 18
# set ff4 = 20

set ff1 = 0.01
set ff2 = 0.1
set ff3 = 5
set ff4 = 10

sac << !
cut $wf_b $wf_e
r ${net}.${stn}.*${chan1}*.SAC
transfer from POLEZERO subtype $PZ_BHZ to wa FREQLIMITS $ff1 $ff2 $ff3 $ff4
cut off
w  append .wa

cut $wf_b $wf_e
r ${net}.${stn}.*${chan2}*.SAC
rtrend
transfer from POLEZERO subtype $PZ_BHN to wa FREQLIMITS $ff1 $ff2 $ff3 $ff4
cut off
w append .wa

cut $wf_b $wf_e
r ${net}.${stn}.*${chan3}*.SAC
rtrend
transfer from POLEZERO subtype $PZ_BHE to wa FREQLIMITS $ff1 $ff2 $ff3 $ff4
cut off
w append .wa
quit
!

sac << !
cut $wf_b $wf_e
r ${net}.${stn}.*${chan1}*.SAC
transfer from POLEZERO subtype $PZ_BHZ to none FREQLIMITS $ff1 $ff2 $ff3 $ff4
cut off
w  append .disp

cut $wf_b $wf_e
r ${net}.${stn}.*${chan2}*.SAC
rtrend
transfer from POLEZERO subtype $PZ_BHN to none FREQLIMITS $ff1 $ff2 $ff3 $ff4
cut off
w append .disp

cut $wf_b $wf_e
r ${net}.${stn}.*${chan3}*.SAC
rtrend
transfer from POLEZERO subtype $PZ_BHE to none FREQLIMITS $ff1 $ff2 $ff3 $ff4
cut off
w append .disp
quit
!

sac << !
cut $wf_b $wf_e
r ${net}.${stn}.*${chan1}*.SAC
transfer from POLEZERO subtype $PZ_BHZ to acc FREQLIMITS $ff1 $ff2 $ff3 $ff4
cut off
w  append .acc

cut $wf_b $wf_e
r ${net}.${stn}.*${chan2}*.SAC
rtrend
transfer from POLEZERO subtype $PZ_BHN to acc FREQLIMITS $ff1 $ff2 $ff3 $ff4
cut off
w append .acc

cut $wf_b $wf_e
r ${net}.${stn}.*${chan3}*.SAC
rtrend
transfer from POLEZERO subtype $PZ_BHE to acc FREQLIMITS $ff1 $ff2 $ff3 $ff4
cut off
w append .acc
quit
!

saclst dist depmax f ${net}.${stn}*${chan1}*.SAC.wa >> vertical.xy 
saclst dist depmax f ${net}.${stn}*${chan2}*.SAC.wa >> horizontal.xy 
saclst dist depmax f ${net}.${stn}*${chan3}*.SAC.wa >> horizontal.xy
saclst dist depmax f ${net}.${stn}*${chan1}*.SAC.acc >> vertical_acc.xy 
saclst dist depmax f ${net}.${stn}*${chan2}*.SAC.acc >> horizontal_acc.xy 
saclst dist depmax f ${net}.${stn}*${chan3}*.SAC.acc >> horizontal_acc.xy
saclst dist depmax f ${net}.${stn}*${chan1}*.SAC.acc >> vertical_disp.xy 
saclst dist depmax f ${net}.${stn}*${chan2}*.SAC.acc >> horizontal_disp.xy 
saclst dist depmax f ${net}.${stn}*${chan3}*.SAC.acc >> horizontal_disp.xy
printf "${net}.${sta}*${chan1}*.SAC.wa  this is where you should check \n"


rm *.wa
rm *.disp
rm *.acc

#r ${net}.${stn}.*${chan2}*.SAC.wa ${net}.${stn}.*${chan3}*.SAC.wa
#rotate to GCP
#w ${net}.${stn}.${chan}R.SAC.wa ${net}.${stn}.${chan}T.SAC.wa

#r ${net}.${stn}.${chan}R.SAC.wa
#ch kcmpnm ${chan}R
#wh


#r ${net}.${stn}.*${chan1}*.SAC
#rtrend
#w ${net}.${stn}.${chan}Z.SAC.wa

#r ${net}.${stn}.${chan}T.SAC.wa
#ch kcmpnm ${chan}T
#wh