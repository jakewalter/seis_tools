#!/bin/bash

thislist1=$1
rm $2
thislist=`tail -n +3 $thislist1`
#echo "$thislist"

while read -r line1
do

echo $line1 | while read line
do
yr=`echo $line | gawk '{print $1}'`
m=`echo $line | gawk '{print $2}'`
mout=`printf "%02.f" $m`
day=`echo $line | gawk '{print $3}'`
dayout=`printf "%02.f" $day`
hr=`echo $line | gawk '{print $4}'`
hrout=`printf "%02.f" $hr`
min=`echo $line | gawk '{print $5}'`
minout=`printf "%02.f" $min`
sec=`echo $line | gawk '{print $6}'`
evla=`echo $line | gawk '{print $7}'`
evlo=`echo $line | gawk '{print $8}'`
evdp=`echo $line | gawk '{print $9}'`
mag=`echo $line | gawk '{print $18}'`
nstas=`echo $line | gawk '{print $10}'`
errox1=`echo $line | gawk '{print $24}'`
errox2=`printf "%0.5s" $errox1`
errox=`printf "%0.2f" $errox2`


printf "$yr$mout$dayout$hrout$minout ${yr} ${m} ${day} ${hr} ${min} ${sec} ${evla} ${evlo} ${evdp} ${mag} ${nstas} ${errox}\n" >> $2
done
done <<< "$thislist"
