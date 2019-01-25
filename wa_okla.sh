#!/bin/sh
day1=1
#day1=274
day2=366
year1=2008
year2=2016
datadir=/disk/cg7/jwalter/okla/day_volumes
cont_outputdir=/disk/cg7/jwalter/okla/ContWaveform
template_outputdir=/disk/cg7/jwalter/okla/TempWaveform1
newdetect_outputdir=/disk/cg7/jwalter/okla/newdetect
work_directory=/disk/cg7/jwalter/okla/working
base_directory=/disk/cg7/jwalter/okla
both_directory=/disk/cg7/jwalter/okla/both
dbname=/disk/cg7/jwalter/okla/okla
#dbname2=/disk/staff/jwalter/southeastAK/ak_cat/db_seak_Oct2013_Mar2013
netcode=OK
minassoc=4

if [ ! -d $template_outputdir ]; then
	mkdir $template_outputdir
fi

if [ ! -d $newdetect_outputdir ]; then
	mkdir $newdetect_outputdir
fi
#####  Make template waveforms using Continuous Waveforms
sacarrivaltime_wa.pl $dbname $cont_outputdir $template_outputdir $netcode $minassoc

CutWaveforms2_wa.bash $work_directory $cont_outputdir $template_outputdir $newdetect_outputdir $dbname

if [ ! -d $both_directory ]; then
	mkdir $both_directory
fi

cp -r $template_outputdir/20* $both_directory
cp -r $newdetect_outputdir/20* $both_directory
cd $both_directory
stationlooper_amp.csh
