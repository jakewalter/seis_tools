#!/bin/sh

input=/home/staff/jwalter/panhandle/hypoDD.relocpanhandle
for counter in `gawk '{print NR}' $input`
do
	oridhypo=`gawk '{if(NR=="'"$counter"'") print $1}' $input`
		#echo dbsubset panhandle.origin "orid==$oridhypo" | dbevproc -p pf/dbevproc.pf -vv - panhandle
	dbsubset pandhandle.origin "orid==$oridhypo" | dbevproc -p pf/dbevproc.pf -v - panhandle
		
done
