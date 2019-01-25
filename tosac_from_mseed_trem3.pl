#!/usr/bin/perl -w


#open(MYFILE,">>dayslist");
#print MYFILE "$i.sac\n";
#close(MYFILE);
#system("ls *$i.sac > $i");
#"/auto/proj/tremor/tremorDB/SEEDVOLUMES/day_volumes";

$files = "/auto/proj/tremor3/oct2009/tremorDB2009/SEEDVOLUMES/data_files_archive1";
$put = "/auto/proj/jwalter/tremor/sac";
$f = 1;
$fmax = 365;

while ($f <= $fmax) {
$fday = sprintf("%03d",$f);
`ls -1 $files/*/*HE.2009.*$fday > $put/F2`;



open(TABLEA,"$put/F2");
@tablea = <TABLEA>;
@name = <TABLEA>;

$i = 0;
while ($i < @tablea) { 
      chomp (@tablea[$i]);
	($field0, $field1,$field2,$field3,$field4,$field5,$field6,$field7,$sta,$file1) = split '/', $tablea[$i];
	($field1,$field2,$field3,$chan,$year,$day) = split "\\.", $file1;
	$names = $sta . $chan . $year . $day . '.sac';
	print "$names\n";
	$loc = $put . '/' . $names;
	#chdir $sta;
	system("ms2sac -G 100000 $tablea[$i] > $loc");
	#chdir $files;


$i = $i + 1;
}
$f++;
}

close(TABLEA);
