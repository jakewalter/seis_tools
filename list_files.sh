#!/bin/sh
month1=1
#day1=274
month2=12
year1=2004
year2=2018
#datadir=/disk/staff/jwalter/tamnet/day_volumes
#cont_outputdir=/disk/staff/jwalter/tamnet/ContWaveform
#template_outputdir=/disk/staff/jwalter/tamnet/TempWaveform
cd /data/okla/ContWaveform2
for yeari in $(gawk 'BEGIN{for(i='$year1';i<='$year2';i+=1)print i}')
do	
	for monthi in $(gawk 'BEGIN{for(i='$month1';i<='$month2';i+=1)print i}')
	do
		monthi2=`printf "%02d" $monthi`		
		ls -d $yeari$monthi2* > list$yeari-$monthi2	
		echo $monthi2
	done
done
#find . -size 0 -delete
cp list* /scratch/okla/working
cd /scratch/okla/working
for f in list*
do
	echo $f
	./run_multiple.sh $f &
done
