#!/bin/sh
day1=308
#day1=274
day2=366
year1=2017
year2=2017
#datadir=/disk/staff/jwalter/tamnet/day_volumes
#cont_outputdir=/disk/staff/jwalter/tamnet/ContWaveform
#template_outputdir=/disk/staff/jwalter/tamnet/TempWaveform

hr1=0
hr2=23
#if [ ! -d $cont_outputdir ]; then
#	mkdir $cont_outputdir
#fi
#seiscomp start caps
DBFLAG="mysql://sysop:sysop@localhost/seiscomp3"
VERBOSITY="-v"
scxmldump -fI -o inventory.xml -d $DBFLAG $VERBOSITY
scxmldump -fC -o config.xml -d $DBFLAG $VERBOSITY
for yeari in $(gawk 'BEGIN{for(i='$year1';i<='$year2';i+=1)print i}')
do	
	for dayi in $(gawk 'BEGIN{for(i='$day1';i<='$day2';i+=1)print i}')
	do
		echo $day
		month=`date -d "$yeari-01-01 +$dayi days -1 day" "+%m"`;
		day=`date -d "$yeari-01-01 +$dayi days -1 day" "+%d"`;
			for hr in $(gawk 'BEGIN{for(i='$hr1';i<='$hr2';i+=1)print i}')
			do	
				#hrplus=`cat $hr + 1 | wc -l`
				
				echo "Time to start a new run!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" $yeari $month $day $hr $((hr+1)) $min
				seiscomp start caps
				sleep 1.5
				echo "$yeari,$month,$day,$hr,00,00 $yeari,$month,$day,$((hr+1)),02,00 * * * *" | capstool -H localhost:18002 -o temp.mseed
				offline-playback_mix.sh temp.mseed
				rm temp.mseed
			done
	done
	
done
