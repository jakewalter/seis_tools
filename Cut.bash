#!/bin/bash

for template in `gawk '{ print $1}' TemplateList.dat`
do
	cont=`echo $template | gawk '{print substr($1,1,8)}'`
	cont_btime=`echo $cont | gawk '{print substr($1,1,4)"/"substr($1,5,2)"/"substr($1,7,2),"00:00:00"}' | epoch | gawk '{print $1}'`
	otime=`echo $template |  gawk '{print substr($1,1,4)"/"substr($1,5,2)"/"substr($1,7,2),substr($1,9,2)":"substr($1,11,2)":"substr($1,13,2)}' | epoch | gawk '{print $1}'`
	btime=`echo $cont_btime $otime | gawk '{print $2-$1-30}'`
	etime=`echo $cont_btime $otime | gawk '{print $2-$1+30}'`
	echo $btime $etime $cont | gawk '{print "cut "$1,$2"\nr ../ContWaveforms/"$3"/YC*SAC\nw append 2"}' | sac
	cp ../ContWaveforms/$cont/YC*SAC2 $template/
	year=`echo $template | gawk '{print substr($1,1,4)}'`
	month=`echo $template | gawk '{print substr($1,5,2)}'`
	day=`echo $template | gawk '{print substr($1,7,2)}'`
	hour=`echo $template | gawk '{print substr($1,9,2)}'`
	min=`echo $template | gawk '{print substr($1,11,2)}'`
	sec=`echo $template | gawk '{print substr($1,13,2)}'`
	msec=`echo $template | gawk '{print substr($1,15,2)}'`
	gsact $year $month $day $hour $min $sec $msec f $template/YC*SAC2 | gawk '{printf "r %s\nch o %.4f\nwh\n",$1,$2} END {print "quit"}' | sac
	saclst o f $template/YC*SAC2 | gawk '{printf "r %s\nch allt %.5f\nwh\n",$1,$2*(-1)} END {print "quit"}' | sac
	
done 
