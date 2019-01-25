#!/usr/bin/perl -w


#open(MYFILE,">>dayslist");
#print MYFILE "$i.sac\n";
#close(MYFILE);
#system("ls *$i.sac > $i");


$files = "/auto/proj/tremor4/tremorDB2008/SEEDVOLUMES/data_files_archive";
$put = "/auto/home/jwalter/CRmti/looke2";
$f = 218;
$fmax = 218;
$year1 = 2008;

while ($f <= $fmax) {

`ls $files/*/*BHZ.$year1.*$f* > $put/F2`;



open(TABLEA,"$put/F2");
@tablea = <TABLEA>;

$i = 0;
while ($i < @tablea) { 

chomp (@tablea[$i]);
($field1,$field2,$field3,$field4,$field5,$field6,$field7,$sta,$file1) = split '/', $tablea[$i];
($field1,$field2,$field3,$chan,$year,$day) = split "\\.", $file1;
$newname = $year . '.' . sprintf("%03d",$day) . '.' . $sta . '.BH' . substr($chan,2,2)  . '.SAC';
$loc = $put . '/' . $newname;
system("ms2sac -G 10000000 $tablea[$i] > $loc");
`sac << END
r $newname
transfer from evalresp to vel freqlimits .004 .008 40 50
bp c 1 3 n 4 p 2
interpolate delta .1
mul 1e-9
w $newname
quit
END
`;

	


$i = $i + 1;
}
$f++;
}


close(TABLEA);
system("changeloc_station_cr_v2.pl");
