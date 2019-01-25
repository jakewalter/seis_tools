#!/bin/bash

jday=$1
input=$2

epoch=`echo $jday | gawk '{print "julian -j "substr($1,5,3),substr($1,1,4)}' | sh | gawk '{print $3"/"$1"/"$2,"22:40:00"}' |\
 gawk '{print "echo "$1,$2" | ./epoch"}' | sh | gawk '{printf"%.4f\n", $1}'`

#more echo $epoch
for counter in `gawk '{print NR}' $input`
do
   otime=`gawk '{if(NR=="'"$counter"'") print $1}' $input`
   cc=`gawk '{if(NR=="'"$counter"'") print $2}' $input` 
   template=`gawk '{if(NR=="'"$counter"'") print $3}' $input`
   ratio=`gawk '{if(NR=="'"$counter"'") print $5}' $input`
   kzdate=`echo $otime $epoch | gawk '{printf"%s %.2f\n","epoch",$1+$2}' | sh | gawk '{printf"%s\n",$3}'`
   kztime=`echo $otime $epoch | gawk '{printf"%s %.2f\n","epoch",$1+$2}' | sh | gawk '{printf"%.11s\n",$4}'`
   amp_ratio=`gawk '{if(NR=="'"$counter"'") print $9}' $input`
   nstas=`gawk '{if(NR=="'"$counter"'") print $10}' $input`
   echo "$amp_ratio $kztime"
   gawk '{if($1=='"$template"') printf"%8d %12.2f %5.3f %7.2f %5.2f %5.2f %2d %2d %2d %2d %6.3f %10d %10.5f %10.5f %7.3f %5.2f %2d\n",'"$jday"','"$otime"','"$cc"','"$ratio"',$11+log('"$amp_ratio"')/log(10),$1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,'"$nstas"'}' catalog >> 15times_$jday.catalog

done
