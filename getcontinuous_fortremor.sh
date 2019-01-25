#!/bin/sh
day1=150
day2=250
datadir=/disk/staff/jwalter/mendenhall/day_volumes
cont_outputdir=/disk/staff/jwalter/mend12quake/cont_nofilt
dbname=/disk/staff/jwalter/mendenhall/mend12
netcode=YY

if [ ! -d $cont_outputdir ]; then
	mkdir $cont_outputdir
fi

#### Make Continous waveforms  % check for 2012 compatibility
tosac_from_msd_db2sac_nofilt.pl $day1 $day2 $datadir $cont_outputdir $dbname $netcode

num=$(awk 'BEGIN{for(i='$day1';i<='$day2';i+=1)print i}')
year1=2012
for i in $num
do
year=`date -d "$year1-01-01 +$i days -1 day" "+%Y"`;
month=`date -d "$year1-01-01 +$i days -1 day" "+%m"`;
day=`date -d "$year1-01-01 +$i days -1 day" "+%d"`;
dir=`date -d "$year1-01-01 +$i days -1 day" "+%Y%m%d"`;
echo $year $month $day
gsact $year $month $day 00 00 00 00 f $outputdir/$dir/*.SAC* | gawk '{printf "r "$1"\nch o "$2"\nwh\n"} END{print "quit"}' | sac
saclst o f $outputdir/$dir/*.SAC* | gawk '{printf "r %s\nch allt %.5f\nwh\n",$1,$2*(-1)} END{print "quit"}' | sac
#saclst f ../$dir/*.SAC* | gawk '{printf "cut 100 86300\nr %s\nw over\n",$1} END{print "quit"}' | sac
done
