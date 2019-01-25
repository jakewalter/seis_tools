#!/bin/sh
rm axial2auto
day1=1
day2=366
year=2015
num=$(awk 'BEGIN{for(i='$day1';i<='$day2';i+=1)print i}')
#year1=2012
for i in $num
do
	day=$i;
	day1=$(($i+1));
	echo $day $day1
	db2hypoDDphase.pl /disk/cg7/jwalter/axial/axial2 axial2_$day $year-$day $year-$day1	
done
cat axial2_* > axial2auto
rm axial2_*
