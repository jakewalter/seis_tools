#!/bin/sh
day1=1
#day1=274
day2=366
year1=2008
year2=2016
datadir=/disk/cg7/jwalter/west_texas/day_volumes
cont_outputdir=/disk/cg7/jwalter/west_texas/ContWaveform1
template_outputdir=/disk/cg7/jwalter/west_texas/TempWaveform2
newdetect_outputdir=/disk/cg7/jwalter/west_texas/newdetect
work_directory=/disk/cg7/jwalter/west_texas/working
base_directory=/disk/cg7/jwalter/west_texas
both_directory=/disk/cg7/jwalter/west_texas/both
dbname=/disk/cg7/jwalter/west_texas/west_texas
#dbname2=/disk/staff/jwalter/southeastAK/ak_cat/db_seak_Oct2013_Mar2013
netcode=TX
minassoc=4

if [ ! -d $template_outputdir ]; then
	mkdir $template_outputdir
fi

if [ ! -d $newdetect_outputdir ]; then
	mkdir $newdetect_outputdir
fi
#####  Make template waveforms using Continuous Waveforms
sacarrivaltime_wa.pl $dbname $cont_outputdir $template_outputdir $netcode $minassoc

CutWaveforms2_gpu_wa.bash $work_directory $cont_outputdir $template_outputdir $newdetect_outputdir $dbname

if [ ! -d $both_directory ]; then
	mkdir $both_directory
fi

cp -r $template_outputdir/20* $both_directory
cp -r $newdetect_outputdir/20* $both_directory
cd $both_directory
stationlooper_amp.csh
