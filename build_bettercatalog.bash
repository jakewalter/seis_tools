#!/bin/bash

ls -d 9times_2015* > templist1
thislist1=templist1

while read -r line
do
days1=`echo $line | awk -F"_" '{print $2}'`
days=`echo $days1 | awk -F"." '{print $1}'`
#echo "$thislist"
echo "Prepping for day $days"
prepare_catalog.bash $days
echo "Expanding for day $days"
expand_catalog.bash $days HRSN_stack_detection_mag_MAD_9_final_uniq_clean_amp_ratio.dat
find . -maxdepth 1 -name "amp_20*" -print0 | xargs -0 rm
rm amp_20*
done < "$thislist1"
