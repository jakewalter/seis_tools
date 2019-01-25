#!/bin/bash

#inputcatdir=$1
contdir=$1
#templatedir=$3
outputdir=$2

neworigid=60000
cd $outputdir
#rm -f 15timesall.cat
#cat $inputcatdir/15times* > 15timesall.cat
input=~/tempsue/events_2_above_need.txt
#input=15timesall.cat

for counter in `gawk '{print NR}' $input`
do
	#cont=`gawk '{if(NR=='"$counter"') print $1}' $input`
	#year=`gawk '{if(NR=='"$counter"') printf"%s%s%s\n",substr($0,1,4)' $input`
	#month=`gawk '{if(NR=='"$counter"') printf"%s%s%s\n",substr($0,5,2)' $input`
 	#template1=`gawk '{if(NR=='"$counter"') print $6}' $input`
	#template=$(printf %12d $template1)
	#new_id=`gawk '{if(NR=='"$counter"') printf"%s%s%s%s%s%s\n",substr($0,1,4),substr($0,6,2),substr($0,9,2),substr($0,12,2),substr($0,15,2),substr($0,18,2)}' $input`
	#otime=`gawk '{if(NR=='"$counter"') print $2}' $input`
	#yearmonthday=`gawk '{if(NR=='"$counter"') printf"%s%s%s\n",substr($0,1,4),substr($0,5,2),substr($0,7,2)}' $cont`
        #templat=`gawk '{if(NR=='"$counter"') print $14}' $input`
	#templon=`gawk '{if(NR=='"$counter"') print $15}' $input`
	#tempdepth=`gawk '{if(NR=='"$counter"') print $16}' $input`
	yearmonthday=`gawk '{if(NR=='"$counter"') printf"%s%s%s\n",substr($1,1,4),substr($1,5,2),substr($1,7,2)}' $input`
	hour=`gawk '{if(NR=='"$counter"') printf"%s\n",substr($1,9,2)}' $input`
	min=`gawk '{if(NR=='"$counter"') printf"%s\n",substr($1,11,2)}' $input`
	#dayseconds=`gawk '{if(NR=='"$counter"') print $2}' $input`
	hrsec=`echo "$hour/24" | bc -l`
        minsec=`echo "($min/1440)" | bc -l`
	daysecondsa=`echo "scale=0;($hrsec+$minsec)*86400" | bc -l`
	dayseconds=`echo $daysecondsa | gawk '{print int($1)}'`
	#echo $hr $min $sec $yearmonthday
	#new_id=$cont$(printf %02d $hr)$(printf %02d $min)$(printf %02d $sec)
	btime=`echo "scale=0;$dayseconds-0" | bc -l`
	etime=`echo "scale=0;$dayseconds+120" | bc -l`
	#t2template=`saclst t2 f $templatedir/$template | gawk '{print $2}'`
	
	#echo $new_id $cont $t2template
#	mkdir $yearmonthday$hour$min
	echo $dayseconds $btime $etime $yearmonthday
if [[ -d $contdir/$yearmonthday ]]; then
	mkdir $yearmonthday$hour$min
	cd $contdir/$yearmonthday
	pwd
for i in *bp
do
#echo $btime $etime
echo $outputdir/$yearmonthday$hour$min/$i
onegsecondsday=`echo "$dayseconds*(-1)" | bc -l`

sac << EOF
cut b $btime $etime
r $i
ch o $dayseconds
ch allt $onegsecondsday
w $outputdir/$yearmonthday$hour$min/$i
quit
EOF
done
#cp $templatedir/$template/origid.dat $outputdir/$new_id/ 
#printf "%d" "$neworigid" > $outputdir/$new_id/origid.dat
#neworigid=$(($neworigid+1))
cd $outputdir
fi
#ls $contdir/$cont/*bp | gawk -F"/" '{print "cut "'"$btime"','"$etime"'"\nr "$0"\nw $outputdir/"'"$new_id"'"/"$NF} END {print "quit"}' | sac
done
