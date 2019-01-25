#!/bin/sh
year1=2008
year2=2011

datadir=/disk/staff/jwalter/bakken/day_volumes
cont_outputdir=/disk/cg5/jwalter/bakken/ContWaveform
template_outputdir=/disk/cg5/jwalter/bakken/TempWaveform
dbname=/disk/staff/jwalter/bakken/bakkendb
#dbname2=/disk/staff/jwalter/southeastAK/ak_cat/db_seak_Oct2013_Mar2013
netcode=ZZ
minassoc=6

num=$(gawk 'BEGIN{for(i='$year1';i<='$year2';i+=1)print i}')

#db2STNS_bakken_v1.pl /disk/staff/jwalter/bakken/bakkendb bakken.STNS

for year in $num
do	
	sacarrivaltime_fromcont_v2_bakken.pl /disk/staff/jwalter/bakken/bakkendb$year $cont_outputdir $template_outputdir $netcode $minassoc
	
#db2hypoDDphase.pl /disk/staff/jwalter/bakken/bakkendb$year hypoddpickspha$year $year-001 $year-366
done
