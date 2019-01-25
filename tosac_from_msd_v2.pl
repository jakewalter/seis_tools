#!/usr/bin/perl -w


#open(MYFILE,">>dayslist");
#print MYFILE "$i.sac\n";
#close(MYFILE);
#system("ls *$i.sac > $i");
#"/auto/proj/tremor/tremorDB/SEEDVOLUMES/day_volumes";

$files = "/home/jwalter9/mendenhall_data/seismic/day_volumes";
$put = "/home/jwalter9/mendenhall_data/all";
$f = 1;
$fmax = 365;

while ($f <= $fmax) {
$fday = sprintf("%03d",$f);
`ls -1 $files/*/*E*$fday > $put/F2`;



open(TABLEA,"$put/F2");
@tablea = <TABLEA>;
@name = <TABLEA>;

$i = 0;
while ($i < @tablea) { 
      chomp (@tablea[$i]);
	($field0, $field1,$field2,$field3,$field4,$field5,$sta,$file1) = split '/', $tablea[$i];
	($field1,$field2,$field3,$chan,$year,$day) = split "\\.", $file1;
	$names = $sta . $chan . $year . $day . '.sac';
	print "$names\n";
	$loc = $put . '/' . $names;
	#chdir $sta;
	system("ms2sac -G 100000 $tablea[$i] > $loc");
	#chdir $files;

#transfer from evalresp to vel freqlimits .004 .008 10 20


$i = $i + 1;
}
$f++;
}

close(TABLEA);
