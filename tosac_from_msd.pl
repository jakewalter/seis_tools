#!/usr/bin/perl -w


#open(MYFILE,">>dayslist");
#print MYFILE "$i.sac\n";
#close(MYFILE);
#system("ls *$i.sac > $i");
#"/auto/proj/tremor/tremorDB/SEEDVOLUMES/day_volumes";

$files = "/home/jwalter9/nicoyaclean/day_volumes";
$put = "/home/jwalter9/nicoyaquake";
#$f = 220;
#$fmax = 300;
$f = $ARGV[0];
$fmax = $ARGV[1];


if (  @ARGV < 2 )
 { die ( "Usage: $0 day1 day2 " ); 
}

while ($f <= $fmax) {
$fday = sprintf("%03d",$f);
`ls -1 $files/*/*H*$fday > $put/F2`;

system("mkdir $put/$fday");

open(TABLEA,"$put/F2");
@tablea = <TABLEA>;
@name = <TABLEA>;

$i = 0;
while ($i < @tablea) { 
      chomp (@tablea[$i]);
	($field0, $field1,$field2,$field3,$field4,$sta,$file1) = split '/', $tablea[$i];
	($field1,$field2,$field3,$chan,$year,$day) = split "\\.", $file1;
	#$names = $sta . $chan . $year . $day . '.sac';
	$names = 'YZ.' . $sta . '.' . $chan . '.SAC';
	print "$names\n";
	$loc = $put . '/' . $fday . '/' . $names;
	#$fpath = $put . '/' . $fput;
	#chdir $sta;
	system("ms2sac -G 100000 $tablea[$i] > $loc");
#	system("mkdir $put/$fday");
#chdir $files;
`sac << END
r $loc
rmean
transfer from RESPDIR/evalresp to none freqlimits .002 .005 40 45
interpolate delta 0.01
bp c 5 15 n 4 p 2
w $loc.bp
quit
END
`;
`rm $loc`;


$pts0=`saclst npts f $loc.bp`;
($blah,$pts)=split(/\s+/, $pts0);
print "$pts\n";
if ($pts < 8600000) {
`rm $loc.bp`;
}

$i = $i + 1;
}
#$begin0=`saclst kzdate f *SAC`;
#($blah,$begin)=split(/\s+/, $begin0);
#($year,$month,$day)=split("/", $begin);


#print "$year $month $day";
#chdir($fpath);
#`gsact $year $month $day 00 00 00 00 f $fpath/*.SAC* | gawk '{printf "r "$1"\nch o "$2"\nwh\n"} END{print "quit"}' | sac`;
#`saclst o f $fpath/*.SAC* | gawk '{printf "r %s\nch allt %.5f\nwh\n",$1,$2*(-1)} END{print "quit"}' | sac`;
#chdir($put);
$f++;
}

close(TABLEA);
system("changeloc_station_cr_v2.pl");
