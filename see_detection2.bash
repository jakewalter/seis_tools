#!/bin/bash


cont=$1

rm -rf 9times_$cont.dat

min_chan_number=12
max_chan_number=35

for template in `gawk '{print $1}' xmeng_temp_list`
do
	num_chan_used=`cat $template/sac_file_SNR_$cont.id | wc -l`
	if [ $num_chan_used -gt $min_chan_number ]; then
		if [ $num_chan_used -lt $max_chan_number ]; then
			gawk '{if(NR>1) print $0,'$template'}' $template/9times_2_8_$cont.dat >> 9times_$cont.dat
			echo "yesssssss"
		fi
	fi
done
