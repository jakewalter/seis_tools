#!/usr/bin/perl -w


#open(MYFILE,">>dayslist");
#print MYFILE "$i.sac\n";
#close(MYFILE);
$datadir = "/auto/home/jwalter/triggerjokul/data";
$tempdir = "/auto/home/jwalter/triggerjokul/Temp";
$contdir = "/auto/home/jwalter/triggerjokul/ContWaveform";
$workdir = "/auto/home/jwalter/triggerjokul/working";
$whichtemp = "temp1";


@comp = <'east' 'north' 'vert'>;
@compa = <'E' 'N' 'Z'>;
$h = 0;
$hmax = 2;
while ($h <= $hmax) {

`ls $datadir/$comp[$h]/*sac > $workdir/F2`;
open(TABLEA,"$workdir/F2");
@tablea = <TABLEA>;
$i = 0;
while ($i < @tablea) { 
chomp ($tablea[$i]);
($field1,$field2,$field3,$field4,$field5,$field6,$compname,$day) = split '/', $tablea[$i];
#($field1,$field2,$field3,$chan,$year,$day) = split "\\.", $file1;

$tempfile = $tempdir . '/' . $whichtemp . '/MG.WINT.' . $compa[$h] . '.SAC';
$contfile = $workdir . '/MG.WINT.' . $compa[$h] . '.SAC';
print "$contfile";
`sac << END

r $tabea[$i]
hp c 1
w $contfile
quit
END`;
# 65 110
`sliding_wfcc_fix_v5 -f $tempfile -s $contfile -b 2 -a 11 -B 1 -A 86400 -S 0.01 -F 1 -o $working/wfcc_$comp[$h]_$day`;

$i = $i + 1;
};
$h = $h + 1;
};

close(TABLEA);
