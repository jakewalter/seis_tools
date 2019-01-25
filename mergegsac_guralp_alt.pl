#!/usr/bin/perl -w


#open(MYFILE,">>dayslist");
#print MYFILE "$i.sac\n";
#close(MYFILE);i
#system("ls *$i.sac > $i");

#$files = "/auto/proj/jwalter/ant08/all";
$put = "/auto/proj/jwalter/ant09/";
$station = '6094';
$year = 2009;
@day = (1..31);
@month = (1..12);
@stalist = ('z', 'e', 'n');
$s = 0;
$d = 0;
$m = 0;
foreach $s (@stalist) {
	foreach $m (@month) {
		foreach $d (@day) { 
		$dayout = sprintf("%02d",$d);
		$monthout = sprintf("%02d",$m);
		$loc = $year . $monthout . $dayout . '_' . $station . '_' . $s . '.sac';
        	print "$loc\n";
		`ls *$s*/$year$monthout$dayout* > temp`;
		open(TABLEA, "temp");
		@tablea = <TABLEA>;
		$howlong = length(@tablea);
if (scalar(@tablea) > 0) {
`gsac << END
r *$s*/$year$monthout$dayout*
rmean
merge
w $loc
quit
END
`;
}
		}
	}
}

`cp ./*.sac $put`;

