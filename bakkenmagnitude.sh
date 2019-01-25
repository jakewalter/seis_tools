#!/bin/sh
year1=2008
year2=2011

num=$(gawk 'BEGIN{for(i='$year1';i<='$year2';i+=1)print i}')

for year in $num
do	
	#cp bakkendb.network bakkendb$year.network
	#cp bakkendb.instrument bakkendb$year.instrument
	#cp bakkendb.snetsta bakkend$year.snetsta
	#cp bakkendb.calibration bakkendb$year.calibration
	#cp bakkendb.sensor bakkendb$year.sensor
	#cp bakkendb.site bakkendb$year.site
	#cp bakkendb.sitechan bakkendb$year.sitechan
	#cp bakkendb.schanloc bakkendb$year.schanloc
	#cp bakkendb.snetsta bakkendb$year.snetsta
	input=/home/staff/jwalter/hypolocate/hypoDD.reloc${year}c
	for counter in `gawk '{print NR}' $input`
	do
   		oridhypo=`gawk '{if(NR=="'"$counter"'") print $1}' $input`
		echo "dbsubset bakkendb$year.origin "orid==$oridhypo" | dbevproc -p pf/dbevproc.pf -vv - bakkendb$year"
		dbsubset bakkendb$year.origin "orid==$oridhypo" | dbevproc -p pf/dbevproc.pf -vv - bakkendb$year
		
	done

done



