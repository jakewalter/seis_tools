#!/bin/bash

inputcatdir=$1
contdir=$2
templatedir=$3
outputdir=$4
originaldatabase=$5

neworigid=60000
cd $outputdir
rm -f 15timesall1.cat
cat $inputcatdir/15times_201* > 15timesall1.cat
#input=~/Nicoya3/15times_20120904.catalog
cat 15timesall1.cat | gawk '$3>0.35' > 15timesall.cat
input=15timesall.cat
rm $outputdir/newevent

for counter in `gawk '{print NR}' $input`
do
	cont=`gawk '{if(NR=='"$counter"') print $1}' $input`
	#year=`gawk '{if(NR=='"$counter"') printf"%s%s%s\n",substr($0,1,4)' $input`
	#month=`gawk '{if(NR=='"$counter"') printf"%s%s%s\n",substr($0,5,2)' $input`
 	template1=`gawk '{if(NR=='"$counter"') print $6}' $input`
	template=$(printf %12d $template1)
	ccvalue=`gawk '{if(NR=='"$counter"') print $3}' $input`
	#new_id=`gawk '{if(NR=='"$counter"') printf"%s%s%s%s%s%s\n",substr($0,1,4),substr($0,6,2),substr($0,9,2),substr($0,12,2),substr($0,15,2),substr($0,18,2)}' $input`
	echo $template $template1
	oldorigid=`gawk '{print $1}' ../templates/$template/origid.dat`
	#$(head -n 1 ./templates/$template/origid.dat)
	echo $oldorigid
#	perl /home/jwalter/bin/db2hyposingle.pl /data3/mendenhall/nicoyaclean/nicclean hypoddnewevent $oldorigid $neworigid
	otime=`gawk '{if(NR=='"$counter"') print $2}' $input`
	#yearmonthday=`gawk '{if(NR=='"$counter"') printf"%s%s%s\n",substr($0,1,4),substr($0,5,2),substr($0,7,2)}' $cont`
        templat=`gawk '{if(NR=='"$counter"') print $14}' $input`
	templon=`gawk '{if(NR=='"$counter"') print $15}' $input`
	tempdepth=`gawk '{if(NR=='"$counter"') print $16}' $input`
	yearmonthday=`gawk '{if(NR=='"$counter"') printf"%s%s%s\n",substr($1,1,4),substr($1,5,2),substr($1,7,2)}' $input`
	year=`gawk '{if(NR=='"$counter"') printf"%s\n",substr($1,1,4)}' $input`
	month=`gawk '{if(NR=='"$counter"') printf"%s\n",substr($1,5,2)}' $input`
	day=`gawk '{if(NR=='"$counter"') printf"%s\n",substr($1,7,2)}' $input`
	dayseconds=`gawk '{if(NR=='"$counter"') print $2}' $input`
	hr=`echo "scale=0;$dayseconds/3600" | bc -l`
        min=`echo "scale=0;($dayseconds/60) - ($hr*60)" | bc -l`
	sec=`echo "scale=0;($dayseconds) - ($min*60) - ($hr*60*60)" | bc -l`
	echo " First test" $year $month $day $hr $min $sec $dayseconds
	perl ~/bin/db2tomosingle.pl $originaldatabase newevent $oldorigid $neworigid $year $month $day $hr $min $sec $dayseconds
	new_id=$cont$(printf %02d $hr)$(printf %02d $min)$(printf %02d $sec)
	btime=`echo "scale=0;$dayseconds-20" | bc -l`
	etime=`echo "scale=0;$dayseconds+40" | bc -l`
	#t2template=`saclst t2 f $templatedir/$template | gawk '{print $2}'`
	
	#echo $new_id $cont $t2template
	mkdir $new_id
	#echo $dayseconds $btime $etime
	cd $contdir/$cont
	pwd
for i in *bp
do
if [[ -f $templatedir/$template/$i ]]; then
	otemplate=`saclst o t1 t2 f $templatedir/$template/$i | gawk '{print $2}'`
	t1template=`saclst o t1 t2 f $templatedir/$template/$i | gawk '$3>0' | gawk '{print $3}'`
	t2template=`saclst o t1 t2 f $templatedir/$template/$i | gawk '$4>0' | gawk '{print $4}'`
	#t1diff=`echo "scale=0;$t1template-$otemplate" | bc -l`
	#t2diff=`echo "scale=0;$t2template-$otemplate" | bc -l`
	if [[ $t1template = "" ]]; then
		flag="t2"
		#fvalue=`echo "$t2diff-$dayseconds" | bc -l`
		fvalue=`echo "$t2template" | bc -l`
	else
		flag="t1"
		fvalue=`echo "$t1template" | bc -l`
	fi
echo $btime $etime
echo $outputdir/$new_id/$i
echo $flag $fvalue $t1template $t2template
unset t1template
unset t2template

onegsecondsday=`echo "$dayseconds*(-1)" | bc -l`

sac << EOF
cut o $btime $etime
r $i
ch evla $templat
ch evlo $templon
ch evdp $tempdepth
ch o $dayseconds
ch $flag $fvalue
ch allt $onegsecondsday
ch $flag $fvalue
w $outputdir/$new_id/$i
quit
EOF
fi
done
#cp $templatedir/$template/origid.dat $outputdir/$new_id/ 
printf "%d" "$neworigid" > $outputdir/$new_id/origid.dat
neworigid=$(($neworigid+1))
cd $outputdir
#ls $contdir/$cont/*bp | gawk -F"/" '{print "cut "'"$btime"','"$etime"'"\nr "$0"\nw $outputdir/"'"$new_id"'"/"$NF} END {print "quit"}' | sac
done
