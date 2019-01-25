#!/bin/sh

	input=/home/staff/jwalter/wyoming/hypoDD.relocwyoming
	for counter in `gawk '{print NR}' $input`
	do
   		oridhypo=`gawk '{if(NR=="'"$counter"'") print $1}' $input`
		echo "dbsubset wyoming.origin "orid==$oridhypo" | dbevproc -p pf/dbevproc.pf -vv - wyoming"
		dbsubset wyoming.origin "orid==$oridhypo" | dbevproc -p pf/dbevproc.pf -vv - wyoming
		#dbsubset wyoming.detection "time>1221163819" | dbgrassoc -pf pf/dbgrassoc.pf -v - wyoming pf/ttgrid
		
	done




