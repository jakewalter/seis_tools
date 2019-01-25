#!/bin/bash

input=$1

rm -rf TimeWindow.dat

for counter in `gawk '{print NR}' $input`
do

otime=`gawk '{if(NR=="'"$counter"'") print $4}' $input`

template=`gawk '{if(NR=="'"$counter"'") print $14}' $input`

btime=`saclst t1 f /data3/sjfz/SJF/TemplateWaveforms/bp/$template/*bp | gawk '{if($2>0) print $2-1}' | sort -n | gawk '{if(NR==1) print $1}'`

etime=`saclst t2 f /data3/sjfz/SJF/TemplateWaveforms/bp/$template/*bp | gawk '{if($2>0) print $2+5}' | sort -n -r | gawk '{if(NR==1) print $1}'`

echo $otime $btime $etime | gawk '{printf"%.2f %.2f\n",$1+$2,$1+$3}' >> TimeWindow.dat

done
