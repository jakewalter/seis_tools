#!/bin/bash

# this version loop through and remove those duplicate detections
# so that there is only 1 event in every 2 s
#if [ $#argv == 1 ]; then
#	input=$1
#else
	input=HRSN_stack_detection_mag_MAD_9_final_uniq.dat
#fi

duplicate_wc=`gawk '{if (NR == 1) {a=$1;b=$2;c=$3;d=$4;e=$5} else {if ($1-a<2) print $0; a=$1;b=$2;c=$3;d=$4;e=$5}}' $input | wc -l | gawk '{print $1}'`
echo $duplicate_wc


tmp1=`echo $input | gawk -F"." '{print $1".tmp1"}'`
tmp2=`echo $input | gawk -F"." '{print $1".tmp2"}'`
tmp3=`echo $input | gawk -F"." '{print $1".tmp3"}'`
tmp4=`echo $input | gawk -F"." '{print $1".tmp4"}'`
tmp5=`echo $input | gawk -F"." '{print $1".tmp5"}'`
tmp6=`echo $input | gawk -F"." '{print $1".tmp6"}'`
output=`echo $input | gawk -F"." '{print $1"_clean.dat"}'`
output_tmp=`echo $input | gawk -F"." '{print $1"_clean.dat.tmp"}'`

counter=1

if [ $duplicate_wc > 1 ]; then
	printf "starting step $counter with duplicate event $duplicate_wc\n"
	gawk '{if (NR>1) print $0}' $input > $tmp1
	wc -l $input | gawk '{print "head -"$1-1,$2}' | sh > $tmp2
	paste -d" " $tmp1 $tmp2 | gawk '{if ($4-$9<=2) print $0}' > $tmp3
	gawk '{printf "%.2f %.3f %s %.2f %.2f\n%.2f %.3f %s %.2f %.2f\n",$1,$2,$3,$4,$5,$6,$7,$8,$9,$10}' $tmp3 > $tmp4
	gawk '{if ($2>=$7) printf "%.2f %.3f %s %.2f %.2f\n",$1,$2,$3,$4,$5; else if ($2<$7) printf "%.2f %.3f %s %.2f %.2f\n",$6,$7,$8,$9,$10}' $tmp3 | sort -n | uniq > $tmp5
	extract $input $tmp4 > $tmp6
	cat $tmp6 $tmp5 | sort -n | uniq > $output_tmp
	cp $output_tmp $input
	old_duplicate_wc=$duplicate_wc
	duplicate_wc=`gawk '{if (NR == 1) {a=$1;b=$2;c=$3;d=$4;e=$5} else {if ($1-a<2) print $0; a=$1;b=$2;c=$3;d=$4;e=$5}}' $input | wc -l | gawk '{print $1}'`
	printf "step $counter finished, old duplicate event $old_duplicate_wc, new duplicate event $duplicate_wc\n"
fi

mv $output_tmp $output
rm -f $tmp1 $tmp2 $tmp3 $tmp4 $tmp5 $tmp6
