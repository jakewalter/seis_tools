#!/usr/bin/perl -w


#open(MYFILE,">>dayslist");
#print MYFILE "$i.sac\n";
#close(MYFILE);
#system("ls *$i.sac > $i");


#$files = "/auto/proj/jwalter/ant08/all";
$put = "/auto/proj/jwalter/ant08/all/all";
$f = 2008330;
$fmax = 2008365;

while ($f <= $fmax) {

$chan = 1;
$chanmax = 6;

while ($chan <= $chanmax) { 
	@stalist = ('9900', 'a703', 'a734', 'a702');
	$k = 0;
	$kmax = 4;
	while ($k <= $kmax) {
	$loc = $f . '_' . $stalist[$k] . '_' . $chan . '.sac';
	#system();
	`gsac << END
	r $f*$stalist[$k]_1_$chan.sac
	merge
	w $loc
	quit
	END
	`;
	$k = $k + 1;
}
$chan = $chan + 1;
}
$f = $f + 1;
}

#close(TABLEA);
