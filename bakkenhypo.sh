#!/bin/sh
year1=2008
year2=2011

num=$(gawk 'BEGIN{for(i='$year1';i<='$year2';i+=1)print i}')

db2STNS_bakken_v1.pl /disk/staff/jwalter/bakken/bakkendb bakken.STNS

for year in $num
do	
	db2hypoDDphase.pl /disk/staff/jwalter/bakken/bakkendb$year hypoddpickspha$year $year-001 $year-366
done
