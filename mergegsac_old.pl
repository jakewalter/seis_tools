#!/usr/bin/perl -w


#open(MYFILE,">>dayslist");
#print MYFILE "$i.sac\n";
#close(MYFILE);i
#system("ls *$i.sac > $i");

#$files = "/auto/proj/jwalter/ant08/all";
$put = "/auto/proj/jwalter/cookieold/";
$station = '6073';
$year = '2007';
@day = (1..31);
@month = (12);
@stalist = ('e');
$s = 0;
$d = 0;
$m = 0;
foreach $s (@stalist) {
	foreach $m (@month) {
		foreach $d (@day) { 
		$dayout = sprintf("%02d",$d);
		$monthout = sprintf("%02d",$m);
		$loc = $year . $monthout . $dayout . '_' . $station . '_' . $s . '.sac';
#        	print "$loc\n";
		`ls *$station$s*/$year$monthout$dayout* > temp`;
		open(TABLEA, "temp");
		@tablea = <TABLEA>;
		$howlong = length(@tablea);
		$temp = $station . $s . '2/' . $year . $monthout . $dayout . '_[01]';
		$temp2 = $station . $s . '2/' . $year . $monthout . $dayout . '_[2]';
if (scalar(@tablea) > 0) {
print "$loc\n";
`gsac << END
r $temp*
rmean
merge
w temp
r temp $temp2*
merge
w $loc
quit
END
`;
}
		}
	}
}

#`cp ./*.sac $put`;

