#!/bin/bash


cont=$1
output_option=2

# 1, output to sac, 0 output to .dat file
# 2 output the script only

wfcc_code="/home/staff/jwalter/bin/sliding_wfcc_fix_v5"

#filter flag
################
filter_flag="bp"
#################


current_pwd=`pwd`
evid=`pwd | gawk -F"/" '{print $NF}'`

printf "$evid\n"
#Network name and component index
#################
#comp_code="BP"
#net="BP"
###############

start_date=`date`


printf "\n\n#### start running sliding_wfcc_all.csh on $start_date\n"

# P and S phase in SAC file
#############
p_phase="t1"
s_phase="t2"
############


# Correlating time window relative to the arrival time
###########
t1=-1
t2=5
###########


# start and end of the noise and signal window
a_phase=`echo $p_phase | gawk '{print substr($1,2,1)}'`
signal_start=`echo $t1 | gawk '{print $1}'`
signal_window=`echo $t1 $t2 | gawk '{print $2-$1}'`
noise_start=`echo $t1 $signal_window | gawk '{print $1-$2}'`


# Time step (20Hz)
###############
slide_win=0.05
###############


###################################################
cont_wf_dir="/disk/cg7/jwalter/dallas/ContWaveform/$cont"
cont_wf_dir1=`echo $cont_wf_dir | gawk -F"/" '{print $NF}'`
####################################################


###############################################################################################################
template_base_dir="/disk/cg7/jwalter/dallas/TempWaveform2"
###############################################################################################################


stn_id="stn.id"
template_dir=`echo $template_base_dir $evid | gawk '{print $1"/"$2}'`


# Only use templates with at least 12 channesl SNR>5
########################################
minimum_wf_cutoff=2
########################################


##########################################################################################################
median_SNR_file="/disk/cg7/jwalter/dallas/TempWaveform2/dir_event_SNR_wc_2012_2_8.dat"
##########################################################################################################
median_SNR=`grep $evid $median_SNR_file | gawk '{print $2,$3}'`
wc_SNR_5=`grep $evid $median_SNR_file | gawk '{print $4}'`
printf "$median_SNR_file $median_SNR $wc_SNR_5 test\n"

wc_SNR_flag=`echo $wc_SNR_5 $minimum_wf_cutoff | gawk '{if ($1>=$2) print 1;else print 0}'`

if [ $wc_SNR_flag == 1 ]; then

    printf "median SNR is $median_SNR, at least $wc_SNR_5 >= 12, do the match filter\n"

    SNR_wf=`echo $template_dir | gawk '{print $1"/wf_SNR.dat"}'`

##############################################################################################################
# set a common start and end time
    wf_cont_start=`saclst b f $cont_wf_dir/*.$filter_flag | gawk '{print $2}' | minmax -C -I1 | gawk '{print $2}'`
    cont_wf_e=`saclst e f $cont_wf_dir/*.$filter_flag | gawk '{print $2}' | minmax -C -I1 | gawk '{print $1}'`

# get the maximum t2
 
    #max_t2=`gawk '{print "saclst t2 f '"$template_dir"'/"$1}' $SNR_wf | sh | sort -n | tail -1 | gawk '{print $2}'`
    max_all=`saclst t2 f $template_dir/*bp | gawk '{print $2}'`
	printf "$cont_wf_e $max_t2 $SNR_wf $max_all check this!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"
	wf_cont_end=`echo $cont_wf_e $max_all | gawk '{print $1-int($2)-1}'`
	#wf_cont_end=$cont_wf_e
	rm templist
	for wf1 in `gawk '{print $1}' $SNR_wf`
	do
		`saclst t2 f $template_dir/$wf1 | gawk '{print $2}' >> templist`
	done
	max_t2=`gawk '{print $1}' templist | sort -n | tail -1`
	#printf "check this!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! $max_allt2\n"
################################################################################################################
           #for wf in `gawk '{if ($1 ~/WMOK/) {print $1}}' $SNR_wf`
    for wf in `gawk '/WMOK/{print $1}' $SNR_wf`	
    do
 	#if [ ~$wf ~/WMOK/ ]; then
		printf "check this!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! $wf Nfsdkjflksjflksjflk\n"   
		stn=`echo $wf | gawk -F"." '{print $2}'`
		comp=`echo $wf | gawk -F"." '{print $3}'`
                 printf "check this!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! $comp Nfsdkjflksjflksjflk\n"
		template_wf=`echo $template_dir $wf | gawk '{print $1"/"$2}'`
                cont_wf=`echo $cont_wf_dir $wf | gawk '{print $1"/"$2}'`
                template_wf_SNR=`gawk '{if ($1 == "'"$wf"'") print $2}' $SNR_wf`
                echo $template_wf $template_wf_SNR
                wf_SNR_flag=`echo $template_wf_SNR | gawk '{if ($1>=2) print 1;else print 0}'`
                echo $wf_SNR_flag
                if [ $wf_SNR_flag == 1 ]; then
                        wf_b_t2_e=`saclst b $s_phase e f $template_wf | gawk '{print $2,$3,$4}'`
                        template_wf_flag=`echo $wf_b_t2_e $t1 $t2 | gawk '{if ($1<$2+$4 && $3>$2+$5) print 1;else print 0}'`
               	else        
                        template_wf_flag=0
                fi
		template_wf_flag=1
		if [ $template_wf_flag == 1 ]; then
                        printf "computing sliding_wfcc for $stn $comp wf $cont_wf with template $template_wf\n"
			channel_flag=`echo $comp | gawk '{if(substr($1,3,1)==1) print 0;else if(substr($1,3,1)==2) print 0; else print 1}'`
			#channel_flag=`echo $comp | gawk '{if(substr($1,3,1)==2) print 1;else print 0}'`
			if [ $channel_flag == 0 ]; then
                        	arr=`saclst $s_phase f $template_wf | gawk '{print $2}'`
			else
				arr=`saclst $p_phase f $template_wf | gawk '{print $2}'`
			fi

			printf "check this!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! $arr Nfsdkjflksjflksjflk\n\n\n\n\n"
                        tt1=`echo $arr $t1 | gawk '{printf "%.4f\n",$1+$2}'`
                        tt2=`echo $arr $t2 | gawk '{printf "%.4f\n",$1+$2}'`
                        echo $tt1 $tt2 $wf_cont_start $wf_cont_end
                        if [ $output_option == 0 ]; then
                                tmp_outfile=`echo $stn $comp $cont_wf_dir1 $s_phase $filter_flag | gawk '{print $1"_"$2"_"$3"_"$4"_"$5"_wfcc.dat"}'`
                        else
                                tmp_outfile=`echo $stn $comp $cont_wf_dir1 $s_phase $filter_flag $cont | gawk '{print $1"_"$2"_"$3"_"$4"_"$5"_"$6"_wfcc.sac"}'`
                        fi
                        start_date=`date`
                        if [ $output_option == 1 ]; then
                                $wfcc_code -f $template_wf -s $cont_wf -b $tt1 -a $tt2 -B $wf_cont_start -A $wf_cont_end -S $slide_win -O $tt1 -F $output_option -o $tmp_outfile
                        elif [ $output_option == 0 ]; then
                                $wfcc_code -f $template_wf -s $cont_wf -b $tt1 -a $tt2 -B $wf_cont_start -A $wf_cont_end -S $slide_win -O $tt1 -F $output_option > $tmp_outfile
                        elif [ $output_option == 2 ]; then
                                printf "$wfcc_code -f $template_wf -s $cont_wf -b $tt1 -a $tt2 -B $wf_cont_start -A $wf_cont_end -S $slide_win -O $tt1 -F 1 -o $tmp_outfile\n"
                                $wfcc_code -f $template_wf -s $cont_wf -b $tt1 -a $tt2 -B $wf_cont_start -A $wf_cont_end -S $slide_win -O $tt1 -F 1 -o $tmp_outfile
			fi
                        end_date=`date`
                        printf "start on $start_date, end on $end_date\n"
                fi
	#fi

    done 
  


ls *$cont*wfcc.sac > sac_file_SNR_$cont.id
nummmm=`ls *$cont*wfcc.sac | wc -l`

/home/staff/jwalter/bin/XmengStackShift sac_file_SNR_$cont.id $nummmm 1 shift_2_8_$cont.sac > 9times_2_8_$cont.dat

end_date=`date`


#rm -rf *$cont*wfcc.sac

printf "\n\n#### end running sliding_wfcc_all.csh on $end_date\n"

fi



