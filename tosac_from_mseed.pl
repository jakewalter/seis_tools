#!/usr/bin/perl -w


#open(MYFILE,">>dayslist");
#print MYFILE "$i.sac\n";
#close(MYFILE);
#system("ls *$i.sac > $i");


$files = "/auto/proj/tremor/tremorDB/SEEDVOLUMES/day_volumes";
$put = "/auto/proj/jwalter/tremor/sac";
$f = 1;
$fmax = 365;

while ($f <= $fmax) {

`ls -1 $files/*/*BHE.2008.*$f* > $put/F2`;



open(TABLEA,"$put/F2");
@tablea = <TABLEA>;
@name = <TABLEA>;

$i = 0;
while ($i < @tablea) { 
      chomp (@tablea[$i]);
	($field1,$field2,$field3,$field4,$field5,$field6,$field7,$sta,$file1) = split '/', $tablea[$i];
	($field1,$field2,$field3,$chan,$year,$day) = split "\\.", $file1;
	$names = $sta . $chan . $year . $day . '.sac';
	$loc = $put . '/' . $names;
	#chdir $sta;
	system("ms2sac -G 100000 $tablea[$i] > $loc");
	#chdir $files;


$i = $i + 1;
}
$f++;
}

close(TABLEA);
