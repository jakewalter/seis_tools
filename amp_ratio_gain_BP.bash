#!/bin/bash
# estimate peak amplitude ratio between pairs of matched stations
# use the median value as the proxy for the magnitude

# this version tries to divide the gain to remove potential change
# of the gain over time

#if [ $#argv == 2 ]; then
        evid=$1
	match_time=$2
        cont=$3
#else if [ $#argv == 1 ]; then
#	evid=20010920200602
#	match_time=$1
#else
#	evid=20010920200602
#	match_time=242156.24
#fi
###############
filter_flag="bp"         ################################################### bp, bp3

############################################
working_dir="/home/jwalter/Nicoya4/working"

current_pwd=`pwd`
# set evid = `pwd | gawk -F"/" '{print $NF}'`
year=`echo $evid | gawk '{print substr($1,1,4)}'`
jday=`echo $evid | gawk '{print "julian -d "substr($1,5,2),substr($1,7,2),substr($1,1,4)}' | sh | gawk '{print $1}'`

# set epoch_temp = `printf "$evid\n" | gawk '{print substr($1,1,4)"/"substr($1,5,2)"/"substr($1,7,2),substr($1,9,2)":"substr($1,11,2)":"substr($1,13,2)".00"}' | epoch | gawk '{print $1}'`
#epoch_temp=`gawk '{if ($1 == "'"$evid"'") print $14}' /data1/zpeng_data/Virginia_EQ_08232011/Catalog/ANSS_082011_CEUS_epoch_dist_M58.dat`         ############## catalog

#################
#gain_table="/data/parkfield/RESP/BP_resp_gain.dat"                              ########### Commented out since we dont have a gain table
# note: since all the gain value is negative, we use lsac2 to find
# out the minimum value

# set epoch_continous = `printf "2004/09/29 00:00:00\n" | epoch | gawk '{print $1}'`
#############################
#epoch_cont="1071878400.00"

comp_code="BH"
net="YZ"
############################

cont_wf_dir="/data3/mendenhall/nicoyaquake/ContWaveform/$cont"
#cont_wf_dir="/home/xmeng/DEC_14"
template_base_dir="/data3/mendenhall/nicoyaquake/TempWaveform"

template_wf_dir=`echo $template_base_dir $evid | gawk '{print $1"/"$2}'`

output=`echo $working_dir $evid $match_time | gawk '{print $1"/amp_"$2"_ratio_"$3"_gain.dat"}'`
#if [ ! -e $output ]; then
	rm -f $output
#echo Got it!
#fi


wf_SNR_dat=`echo $template_wf_dir | gawk '{print $1"/wf_SNR.dat"}'`    #################################### wf_SNR.dat, wf_SNR3.dat

for wf in `gawk '{if ($2>=5) print $1}' $wf_SNR_dat`
do

# check if the continous waveform exists
	stn=`echo $wf | gawk -F"." '{print $2}'`
	chan=`echo $wf | gawk -F"." '{print $3}'`
	flag=`echo $chan | gawk '{if(substr($1,3,1)!="Z") print 0;else print 1}'`
	temp_wf=`echo $template_wf_dir $wf | gawk '{print $1"/"$2}'`
	cont_wf=`echo $cont_wf_dir $wf | gawk '{print $1"/"$2}'`
	if [ -e $cont_wf ]; then
		if [ $flag != 1 ]; then
		temp_wf_peak_amp=`saclst t2 f $temp_wf | gawk '{print "lsac2 "$2-2,$2+2,$1}' | sh | gawk '{print $3}'`
	#	temp_wf_gain=`echo $gain_table $epoch_temp $stn $chan | gawk '{print "gawk '\''{if ($1<="$2" && $2>="$2" && $4 == \""$3"\" && $5 == \""$4"\") print $6}'\''",$1}' | sh`
                temp_wf_gain=1                                                 ################# Set to 1 since we dont have a gain table
#		printf "$gain_table $epoch_temp $stn $chan $temp_wf_gain\n"
		s_arr=`saclst o t2 f $temp_wf | gawk '{print $3-$2}'`
		cont_wf_peak_amp=`echo $cont_wf $match_time $s_arr | gawk '{print "lsac2 "$2+$3-2,$2+$3+2,$1}' | sh | gawk '{print $3}'`
	#	cont_wf_gain=`echo $gain_table $epoch_cont $stn $chan | gawk '{print "gawk '\''{if ($1<="$2" && $2>="$2" && $4 == \""$3"\" && $5 == \""$4"\") print $6}'\''",$1}' | sh`
                cont_wf_gain=1
		echo $wf $temp_wf_peak_amp $cont_wf_peak_amp $temp_wf_gain $cont_wf_gain | gawk '{printf "%s %e %e %e\n",$1,($3/$5)/($2/$4),($2/$4),($3/$5)}' >> $output
		fi
		if [ $flag == 1 ]; then
                temp_wf_peak_amp=`saclst t1 f $temp_wf | gawk '{print "lsac2 "$2-2,$2+2,$1}' | sh | gawk '{print $3}'`
        #       temp_wf_gain=`echo $gain_table $epoch_temp $stn $chan | gawk '{print "gawk '\''{if ($1<="$2" && $2>="$2" && $4 == \""$3"\" && $5 == \""$4"\") print $6}'\''",$1}' | sh`
                temp_wf_gain=1                                                 ################# Set to 1 since we dont have a gain table
#               printf "$gain_table $epoch_temp $stn $chan $temp_wf_gain\n"
                s_arr=`saclst o t1 f $temp_wf | gawk '{print $3-$2}'`
                cont_wf_peak_amp=`echo $cont_wf $match_time $s_arr | gawk '{print "lsac2 "$2+$3-2,$2+$3+2,$1}' | sh | gawk '{print $3}'`
        #       cont_wf_gain=`echo $gain_table $epoch_cont $stn $chan | gawk '{print "gawk '\''{if ($1<="$2" && $2>="$2" && $4 == \""$3"\" && $5 == \""$4"\") print $6}'\''",$1}' | sh`
                cont_wf_gain=1
                echo $wf $temp_wf_peak_amp $cont_wf_peak_amp $temp_wf_gain $cont_wf_gain | gawk '{printf "%s %e %e %e\n",$1,($3/$5)/($2/$4),($2/$4),($3/$5)}' >> $output
                fi
#		printf "$wf $temp_wf_peak_amp $cont_wf_peak_amp $temp_wf_gain $cont_wf_gain\n"
	fi

done
# 
#fi
#if [ -e $output ]; then
	amp_ratio_median=`gawk '{if ($2>0 && $2!="nan") print $2}' $output | ./getmedian.pl`
	echo $evid $match_time $amp_ratio_median | gawk '{printf "%s %.2f %.5f %2d\n",$1,$2,$3,$4}' 
#fi
