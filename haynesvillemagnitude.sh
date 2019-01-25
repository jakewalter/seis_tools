#!/bin/sh

	input=/home/staff/jwalter/temp1/hypoDD.relochaynesville
	for counter in `gawk '{print NR}' $input`
	do
   		oridhypo=`gawk '{if(NR=="'"$counter"'") print $1}' $input`
		echo "dbsubset haynesville.origin "orid==$oridhypo" | dbevproc -p pf/dbevproc.pf -vv - haynesville"
		dbsubset haynesville2.origin "orid==$oridhypo" | dbevproc -p pf/dbevproc.pf -vv - haynesville2
		#dbsubset wyoming.detection "time>1221163819" | dbgrassoc -pf pf/dbgrassoc.pf -v - wyoming pf/ttgrid
		
	done
