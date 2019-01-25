#!/bin/csh


if ( $#argv == 5 ) then
	set x = $5
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

if (`expr $switcher` > 0) then
	set chan1 = `printf "$chan\n" | gawk '{print $1"Z"}'`
	set chan2 = `printf "$chan\n" | gawk '{print $1"1"}'`
	set chan3 = `printf "$chan\n" | gawk '{print $1"2"}'`
else
	set chan1 = `printf "$chan\n" | gawk '{print $1"Z"}'`
	set chan2 = `printf "$chan\n" | gawk '{print $1"N"}'`
	set chan3 = `printf "$chan\n" | gawk '{print $1"E"}'`
endif

set value=`cat origid.dat`
saclst dist depmax f ${net}.${stn}*${chan1}*.SAC.bp | gawk '{print $1,$2,$3,'"$x"','"$value"'}' >> ../vertical.txt
saclst dist depmax f ${net}.${stn}*${chan2}*.SAC.bp | gawk '{print $1,$2,$3,'"$x"','"$value"'}' >> ../horizontaln.txt
saclst dist depmax f ${net}.${stn}*${chan3}*.SAC.bp | gawk '{print $1,$2,$3,'"$x"','"$value"'}' >> ../horizontale.txt
printf "${net}.${sta}*${chan1}*.SAC.wa  this is where you should check \n"



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
