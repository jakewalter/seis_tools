#!/usr/bin/perl -w
#system("ls *.sac > templist");
$year = 2008;
#$day0 = 324;
#$day = 345;
$forsta = $year . $day;

$i = 2008324;
$max = 2008335;
$f = 20081119;
$fmax = 20081130;
open(TABLEB,"slipslist");
@tableb = <TABLEB>;
#(@dayslip,@secslip) = split ',', @tableb;

while ($i <= $max) {
#$i*3.sac $f*3.sac > $i");
	$day = substr($i, 4, 3);
	foreach $temp1 (@tableb) {
		($dayslip,$secslip) = split ',', $temp1;
		if ($dayslip == $day) {
		$slip = ($secslip);
		#system("$slip\n $day");
		$cut1 = $slip - 500;
		$cut2 = $slip + 1500;
		#open(TABLEC,"$tempsta");
		#@tempsta2 = <TABLEC>;
		#$test = transpose @tempsta2;
		#system("$cut1\n $cut2");
		#system("ls $i*3.sac $f*3.sac > stalist");
`sac << END
r $i*3.sac $f*3.sac
synch
w append test
quit
END
`;
`sac << END
qdp off
cut $cut1 $cut2
r $i*3.sactest $f*3.sactest
bp c .01 .04
sss
prs
quit
END
`;
}
}

$i = $i + 1;
$f = $f + 1;
}
close(TABLEB);
close(TABLEC);
