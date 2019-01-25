#!/bin/bash

file=$1
counter=$2

match_time=`gawk '{if(NR=='"$counter"') print $4}' $file`
evid=`gawk '{if(NR=='"$counter"') print $8}' $file`
cc=`gawk '{if(NR=='"$counter"') print $6}' $file`
ratio=`gawk '{if(NR=='"$counter"') print $7}' $file`
mag=`gawk '{if(NR=='"$counter"') print $5}' $file`
cont=`echo $file | gawk -F"." '{print $1}' | gawk -F"_" '{print $2}'`

####################
plot_temp_flag=1
###################

##########################################################################
cont_dir="/home/xmeng/Tutorial/CPU_WFCC/ContWaveform/$cont"
template_base_dir="/home/xmeng/Tutorial/CPU_WFCC/TempWaveform"
gawk '{print $1}' /home/xmeng/Tutorial/CPU_WFCC/TempWaveform/$evid/wf_SNR.dat > temp2.dat
##########################################################################


ls $cont_dir/*bp | gawk -F"/" '{print $NF}' > temp1.dat
cat temp*.dat | sort -n | uniq -c | gawk '{if($1==2) print $2}' > stn.id
stn_id="stn.id"


PLOT_NAME=`echo $match_time | gawk '{print $1".eps"}'`
NEW_PLOT="-K -P"
MORE_PLOT="-K -O -P"
END_PLOT="-O -P"


############
tt1=-1
tt2=5
############


plot_size3="-JX4.6/8.5"
map_shift3="-Y2"


template_wf_dir=`echo $template_base_dir $evid | gawk '{print $1"/"$2}'`


wf_total=`wc -l $stn_id | gawk '{print $1}'`
ymin=0.5
ymax=`echo $wf_total | gawk '{print $1+1}'`


stn_sort_id="stn_sort.id"


saclst t2 f `gawk -F"_" '{print "'"$template_wf_dir"'/"$1}' $stn_id` | gawk '{print $2,$1}' | sort -n -r | gawk '{print $2,$1}' | gawk -F"/" '{print $NF}' > $stn_sort_id


wf_time_min=`echo $match_time | gawk '{printf "%.2f\n", $1-5}'`
wf_time_max=`gawk '{print $2+10+"'"$match_time"'"}' $stn_sort_id | head -1`

plot_region3=`echo $wf_time_min $wf_time_max $ymin $ymax | gawk '{print "-R"$1"/"$2"/"$3"/"$4}'`
xx=`echo $wf_time_min $wf_time_max | gawk '{print $1-($2-$1)*0.05}'`


gawk '{print "'"$cont_dir"'/"$1" 0",NR,"1p/128/128/128"}' $stn_sort_id | pssac $plot_size3 $plot_region3 $NEW_PLOT -W1 -M0.15 -Ent-3 $map_shift3 -Ba5f1:"Time (s)":S -r -C$wf_time_min/$wf_time_max > $PLOT_NAME

echo -e "$match_time $ymin\n$match_time $ymax" | psxy -JX -R -K -P -O -W1tap/255/0/0 >> $PLOT_NAME


if [ $plot_temp_flag == 1 ]; then
	for counter in `gawk '{print NR}' $stn_sort_id`
	do
		wf=`gawk '{if(NR=="'"$counter"'") print $1}' $stn_sort_id`
		chan_flag=`echo $wf | gawk -F"." '{print $3}' | gawk '{if($1=="BP1") print 1; else print 0}'`
		if [ $chan_flag == 1 ]; then
			saclst t1 f `echo $template_wf_dir/$wf` |\
                        gawk '{print $1,$2,"'"$match_time"'","'"$tt1"'","'"$tt2"'","'"$counter"'"}' |\
                        gawk '{printf "printf \"%s %.2f %f 0.5p/255/2/2 \\n\" | pssac -JX -R -K -O -P -Ent-3 -r -M0.15 -C%.2f/%.2f >> %s\n",$1,$3,$6+0.5,$2+$3+$4,$2+$3+$5,"'"$PLOT_NAME"'"}' | sh
		else
			saclst t2 f `echo $template_wf_dir/$wf` |\
                        gawk '{print $1,$2,"'"$match_time"'","'"$tt1"'","'"$tt2"'","'"$counter"'"}' |\
                        gawk '{printf "printf \"%s %.2f %f 0.5p/255/2/2 \\n\" | pssac -JX -R -K -O -P -Ent-3 -r -M0.15 -C%.2f/%.2f >> %s\n",$1,$3,$6+0.5,$2+$3+$4,$2+$3+$5,"'"$PLOT_NAME"'"}' | sh 
		fi
	done
fi

gawk -F"." '{printf "%f %f 12 0 4 MR %s.%s\n","'"$wf_time_min"'",NR+0.0,$2,$3}' $stn_sort_id |\
pstext -JX -R $MORE_PLOT -N >> $PLOT_NAME

echo $cc | gawk '{printf "%f %f 12 0 0 MR CC=%s\n","'"$match_time"'"-5,"'"$ymax"'"+1,$1}' | pstext -JX -R $MORE_PLOT -N >> $PLOT_NAME
echo $ratio | gawk '{printf "%f %f 12 0 0 MR Ratio=%s\n","'"$match_time"'"+5,"'"$ymax"'"+1.0,$1}' | pstext -JX -R $MORE_PLOT -N >> $PLOT_NAME
echo $mag | gawk '{printf "%f %f 12 0 0 MR Mag=%s\n","'"$match_time"'"+15,"'"$ymax"'"+1,$1}' | pstext -JX -R $MORE_PLOT -N >> $PLOT_NAME
