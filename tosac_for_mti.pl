#!/usr/bin/perl -w


#open(MYFILE,">>dayslist");
#print MYFILE "$i.sac\n";
#close(MYFILE);
#system("ls *$i.sac > $i");


$files = "/auto/proj/tremor4/tremorDB2008/SEEDVOLUMES/data_files_archive";
$put = "/auto/home/jwalter/CRmti/data";
$f = 216;
$fmax = 217;
$year1 = 2008;

while ($f <= $fmax) {

`ls $files/*/*BH*.$year1.*$f* > $put/F2`;



open(TABLEA,"$put/F2");
@tablea = <TABLEA>;

$i = 0;
while ($i < @tablea) { 
chomp (@tablea[$i]);
($field1,$field2,$field3,$field4,$field5,$field6,$field7,$sta,$file1) = split '/', $tablea[$i];
($field1,$field2,$field3,$chan,$year,$day) = split "\\.", $file1;
$names = $year . '.' . sprintf("%03d",$day) . '.00.00.0000.CR.0.' . $sta . '.0.' . substr($chan,2,2)  . '.SAC';
$newname = $names . '_deconv';
$loc = $put . '/' . $names;
system("ms2sac -G 10000000 $tablea[$i] > $loc");
`sac << END
r $names
transfer from evalresp to none freqlimits .004 .008 10 20
bp c .02 .05 p 2
interpolate delta 1.0
w $newname
quit
END
`;

	


$i = $i + 1;
}
system("rm *SAC");
$f++;
}

close(TABLEA);
