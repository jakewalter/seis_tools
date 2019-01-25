#!/bin/bash



	match_time=76739.75      #time of detection,need to change



#####################################
input="shift_20040306191400.sac"              #stacked CC trace file
#####################################

evid=`pwd | gawk -F"/" '{print $NF}'`       #template event ID

year=`echo $evid | gawk '{print substr($1,1,4)}'` #This may not be needed

PLOT_NAME=`echo $input | gawk -F"." '{print $1".eps"}'`

NEW_PLOT="-K -P"
MORE_PLOT="-K -O -P"
END_PLOT="-O -P"


time_min=`echo $match_time | gawk '{print $1-1000}'`
time_max=`echo $match_time | gawk '{print $1+3000}'`

cc_min=-0.2
cc_max=1

#Sliding time window: 1s before and 5s after the P or S wave arrival
tt1=-1
tt2=5


plot_size1="-JX3.5/1.5"
plot_region1=`echo $time_min $time_max $cc_min $cc_max | gawk '{print "-R"$1"/"$2"/"$3"/"$4}'`


plot_size2="-JX1.5l/1.5"

hist=`echo $input | gawk -F"." '{print $1".hist"}'`

bin=0.01
sacdump_slice $time_min $time_max $input | gawk '{print $2}' | pshistogram -Z0 -Io -W$bin > $hist  #histogram of CC value distribution


hist_min=0.5
hist_max=`gawk '{print log($2)/log(10)}' $hist | minmax -C -I0.5 | gawk '{print 10^$2}'`
plot_region2=`echo $hist_min $hist_max $cc_min $cc_max | gawk '{print "-R"$1"/"$2"/"$3"/"$4}'`

cutoff_cc=0.272     #threshold value

######################################
detection_evid=`echo $evid | gawk '{print "9times_shift_20040306191400.dat"}'`     #list of positive detections
######################################


wc_detection=`echo $time_min $time_max $detection_evid  | gawk '{print "gawk '\''{if ($1>="$1" && $1 <="$2") print $1}'\''",$3}' | sh | wc -l`

map_shift1="-Y8.5 -X1.5"
map_shift2="-X3.8"

norm="-M1/0"


sacdump_slice $time_min $time_max $input |\
psxy -W1 $plot_size1 $plot_region1 $NEW_PLOT -Ba1000f200:"Seconds since 20040306191400":/a0.2f0.1:"Mean CC":WeS $map_shift1 > $PLOT_NAME


echo -e "$time_min $cutoff_cc\n$time_max $cutoff_cc" |\
psxy -JX -R $MORE_PLOT -W2tap/255/0/0 >> $PLOT_NAME

gawk '{if(NR>1) print $1,$2}' $detection_evid | psxy -JX -R $MORE_PLOT -Sc0.05 -G0/0/0 >> $PLOT_NAME

echo $detection_evid $match_time |\
gawk '{print "gawk '\''{if ($1 >= "$2-0.5" && $1 < "$2+0.5") print $0}'\''",$1}' | sh |\
psxy -JX -R $MORE_PLOT -Sc0.1 -G255/0/0 >> $PLOT_NAME

echo 75200 1.2 | gawk '{printf "%f %f 14 0 0 MR a)\n",$1,$2}' |\
pstext -JX -R $MORE_PLOT -N >> $PLOT_NAME

pkd_ms_ot="96"
time_min1=`echo $time_min $pkd_ms_ot | gawk '{printf"%.2f\n",$1/3600+$2}'`
time_max1=`echo $time_max $pkd_ms_ot | gawk '{printf"%.2f\n",$1/3600+$2}'`


echo $time_min $time_max $cc_min $cc_max $evid $wc_detection $pkd_ms_ot |\
gawk '{printf "%f %f 14 0 0 MR %s: %d matches\n",($1+$2)/2/3600+$7+0.5,$3+($4-$3)*0.10,$5,$6}' |\
pstext -JX -R$time_min/$time_max/$cc_min/$cc_max $MORE_PLOT -N -Ba1000f200n >> $PLOT_NAME


gawk '{printf "%f %f\n",$2,$1}' $hist |\
psxy $plot_size2 $plot_region2 $MORE_PLOT -Ba1f3p:"Number":/a0.2f0.1:"Median CC":weSn $map_shift2 -W1p >> $PLOT_NAME

echo -e "$hist_min $cutoff_cc\n$hist_max $cutoff_cc" |\
psxy -JX -R $MORE_PLOT -W2tap/255/0/0 >> $PLOT_NAME

echo 1 1.2 | gawk '{printf "%f %f 14 0 0 MR b)\n",$1,$2}' |\
pstext -JX -R $MORE_PLOT -N >> $PLOT_NAME

echo $hist_min $hist_max $cc_min $cc_max $cutoff_cc |\
gawk '{printf "%f %f 14 0 0 MR Threshold\n%f %f 14 0 0 MR CC= %.2f\n",sqrt($1*$2)*10,$3+($4-$3)*0.85,sqrt($1*$2)*10,$3+($4-$3)*0.72,$5}' |\
pstext -JX -R $MORE_PLOT >> $PLOT_NAME

plot_size3="-JX4.6/7"

wf_time_min=`echo $match_time | gawk '{printf "%.2f\n", $1-2}'`
wf_time_max=`echo $match_time | gawk '{printf "%.2f\n", $1+15}'`

#printf "$wf_time_min $wf_time_max\n"

map_shift3="-Y-7 -X-3.45"

#################################
cont_wf_dir="/data3/parkfield/SanSimeon/ContWaveform/kland/20040306191400"       #continuous waveforms directory
#################################

template_base_dir="/data3/parkfield/SanSimeon/TempWaveform/kland"                 #template waveforms directory

template_wf_dir=`echo $template_base_dir $year $evid | gawk '{print $1"/"$3}'`

comp_code="BP"        #component code
net_code="BP"         #network name
filter_flag="bp"     
comp="1"

#################################
stn_id="sac_file_SNR_20040306191400.id2"
#################################

wf_total=`wc -l $stn_id | gawk '{print $1}'`
ymin=0.5
ymax=`echo $wf_total | gawk '{print $1+4}'`

stn_sort_id="stn_sort.id"

#saclst t1 f /data3/parkfield/SanSimeon/TempWaveform/kland/20030613015406/*BP?.SAC.bp | gawk -F"/" '{print $NF}' | gawk '{print $2,$1}' | sort -n -r > temp.dat
#saclst t2 f /data3/parkfield/SanSimeon/TempWaveform/kland/20030613015406/*EHZ.SAC.bp | gawk -F"/" '{print $NF}' | gawk '{print $2,$1}' | sort -n -r >> temp.dat
#saclst t1 f /data3/parkfield/SanSimeon/TempWaveform/kland/20030613015406/*BH?.SAC.bp | gawk -F"/" '{print $NF}' | gawk '{print $2,$1}' | sort -n -r >> temp.dat
#cat temp.dat | sort -n | gawk '{print $2}' > $stn_sort_id


stn_sort_CC="stn_sort_CC.dat"

##################################################
	lsac $match_time `gawk -F"." '{print $2"_"$3"*_20040306191400_t2_bp*_wfcc.sac"}' $stn_sort_id` > $stn_sort_CC
	lsac 76739.70 `gawk -F"." '{print $2"_"$3"*_20040306191400_t2_bp*_wfcc.sac"}' $stn_sort_id` > stn_sort_CC.dat2
	lsac 76739.80 `gawk -F"." '{print $2"_"$3"*_20040306191400_t2_bp*_wfcc.sac"}' $stn_sort_id` > stn_sort_CC.dat3
##################################################

plot_region3=`echo $wf_time_min $wf_time_max $ymin $ymax | gawk '{print "-R"$1"/"$2"/"$3"/"$4}'`
xx=`echo $wf_time_min $wf_time_max | gawk '{print $1-($2-$1)*0.05}'`

gawk '{print "'"$cont_wf_dir"'/"$1" 0",NR,"1p/128/128/128"}' $stn_sort_id | pssac $plot_size3 $plot_region3 $MORE_PLOT -W1 -M0.3 -Ent-3 $map_shift3 -Ba5f1:"Seconds since 20040306191400":S -r -C$wf_time_min/$wf_time_max >> $PLOT_NAME



saclst t2 f `gawk '{print "'"$template_wf_dir"'/"$1}' $stn_sort_id` |\
gawk '{print $1,$2,"'"$match_time"'","'"$tt1"'","'"$tt2"'"}' |\
gawk '{if(substr($1,71,1)!=1 && substr($1,72,1)!=1) printf "printf \"%s %.2f %d 3/255/0/0 \\n\" | pssac -JX -R -K -O -P -M0.3 -Ent-3 -r -C%.2f/%.2f >> %s\n",$1,$3,NR,$2+$3+$4,$2+$3+$5,"'"$PLOT_NAME"'"}' | sh


saclst t1 f `gawk '{print "'"$template_wf_dir"'/"$1}' $stn_sort_id` |\
gawk '{print $1,$2,"'"$match_time"'","'"$tt1"'","'"$tt2"'"}' |\
gawk '{if(substr($1,71,1)==1 || substr($1,72,1)==1) printf "printf \"%s %.2f %d 3/255/0/0 \\n\" | pssac -JX -R -K -O -P -M0.3 -Ent-3 -r -C%.2f/%.2f >> %s\n",$1,$3,NR,$2+$3+$4,$2+$3+$5,"'"$PLOT_NAME"'"}' | sh

yy=`echo $ymax | gawk '{print $1}'`
echo $match_time $ymin $yy | gawk '{printf "%f %f\n%f %f\n",$1,$2,$1,$3-3}' |\
psxy -JX -R $MORE_PLOT -W1tap/0/0/0 >> $PLOT_NAME


gawk -F"." '{printf "%f %f 14 0 0 MR %s.%s\n","'"$wf_time_min"'",NR+0.0,$2,$3}' $stn_sort_id |\
pstext -JX -R $MORE_PLOT -N >> $PLOT_NAME

# remember to add the cross-correlation value

gawk '{printf "%f %f 14 0 0 MR %4.2f\n","'"$wf_time_max"'"+1.5,NR+0.0,$2}' final_CC.dat  |\
pstext -JX -R $MORE_PLOT -N >> $PLOT_NAME

saclst t2 f `gawk -F"_" '{print "'"$template_wf_dir"'/"$1}' $stn_sort_id` |\
gawk '{if(substr($1,71,1)!=1 && substr($1,72,1)!=1) printf "%f %f\n%f %f\n#\n%f %f\n%f %f\n#\n",$2+"'"$tt1"'"+"'"$match_time"'",NR-0.5,$2+"'"$tt1"'"+"'"$match_time"'",NR+0.5,$2+"'"$tt2"'"+"'"$match_time"'",NR-0.5,$2+"'"$tt2"'"+"'"$match_time"'",NR+0.5}' |\
psxy -JX -R $MORE_PLOT -W2p/0/0/0 -M"#" >> $PLOT_NAME

saclst t1 f `gawk -F"_" '{print "'"$template_wf_dir"'/"$1}' $stn_sort_id` |\
gawk '{if(substr($1,71,1)==1 || substr($1,72,1)==1) printf "%f %f\n%f %f\n#\n%f %f\n%f %f\n#\n",$2+"'"$tt1"'"+"'"$match_time"'",NR-0.5,$2+"'"$tt1"'"+"'"$match_time"'",NR+0.5,$2+"'"$tt2"'"+"'"$match_time"'",NR-0.5,$2+"'"$tt2"'"+"'"$match_time"'",NR+0.5}' |\
psxy -JX -R $MORE_PLOT -W2p/0/0/0 -M"#" >> $PLOT_NAME


echo 76735 26 | gawk '{printf "%f %f 14 0 0 MR c)\n",$1,$2}' |\
pstext -JX -R $MORE_PLOT -N >> $PLOT_NAME

