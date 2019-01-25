#!/usr/bin/perl -w
#system("ls *.sac > templist");
$year = 2008;
#$day0 = 324;
#$day = 345;
$forsta = $year . $day;


open(TABLEB,"slipslist");
@tableb = <TABLEB>;
$f = 0;
while ($f < @tableb) {
	($day,$sec) = split ',', $tableb[$f];
	$tempsta = $year . $day;
	$wtemp = $day . $sec;
	$cut1 = $sec - 1000;
	$cut2 = $sec + 1000;
	#system("$tempsta");
	open(TABLEC,"$tempsta");
	@tempsta2 = <TABLEC>;
	$test = transpose @tempsta2;
	system("$test");
	`sac << END
	r @tempsta2'
	synch
	w @tempsta2
	cut $cut1 $cut2
	r @tempsta2
	w $wtemp_@tempsta2
	quit
	END
	`;
	`gsac << END
	r $wtemp_@tempsta2
	prs
	quit
	END
	`;

$f = $f + 1;
}
close(TABLEB);
close(TABLEC);
