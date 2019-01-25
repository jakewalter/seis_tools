#!/bin/sh
day1=221
day2=230
yeari=2014
datadir=/disk/staff/jwalter/helheim/day_volumes
cont_outputdir=/disk/staff/jwalter/helheim/ContWaveform
template_outputdir=/disk/staff/jwalter/helheim/TempWaveform
dbname=/disk/staff/jwalter/helheim/helheim2
#dbname2=/disk/staff/jwalter/southeastAK/ak_cat/db_seak_Oct2013_Mar2013
netcode=HG
minassoc=3


#### Need the following ancillary programs written by Jake: sacarrivaltime_fromcont.pl and tosac_from_msd_db2sac.pl
#### Need the following from 3rd parties: sac (Seismic Analysis Code), db2sac (Antelope program), gsac (Bob Herrmann's CPS tool), gsact (Zhigang Peng), saclst (comes with newer dist. of SAC) 
####


if [ ! -d $cont_outputdir ]; then
	mkdir $cont_outputdir
fi

if [ ! -d $template_outputdir ]; then
	mkdir $template_outputdir
fi


tosac_from_msd_db2sac.pl $day1 $day2 $yeari $datadir $cont_outputdir $dbname $netcode

#### Fix timing so it is uniform
num=$(gawk 'BEGIN{for(i='$day1';i<='$day2';i+=1)print i}')
for i in $num
do
year=`date -d "$yeari-01-01 +$i days -1 day" "+%Y"`;
month=`date -d "$yeari-01-01 +$i days -1 day" "+%m"`;
day=`date -d "$yeari-01-01 +$i days -1 day" "+%d"`;
dir=`date -d "$yeari-01-01 +$i days -1 day" "+%Y%m%d"`;
echo $year $month $day
gsact $year $month $day 00 00 00 00 f $cont_outputdir/$dir/*.SAC* | gawk '{printf "r "$1"\nch o "$2"\nwh\n"} END{print "quit"}' | sac
saclst o f $cont_outputdir/$dir/*.SAC* | gawk '{printf "r %s\nch allt %.5f\nwh\n",$1,$2*(-1)} END{print "quit"}' | sac
#saclst f ../$dir/*.SAC* | gawk '{printf "cut 100 86300\nr %s\nw over\n",$1} END{print "quit"}' | sac
done  #done with timing fix
#done # done with that year

#####  Make template waveforms using Continuous Waveforms
sacarrivaltime_fromcont_v2_helheim.pl $dbname $cont_outputdir $template_outputdir $netcode $minassoc
