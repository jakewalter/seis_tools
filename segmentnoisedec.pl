#!/usr/bin/perl -w


#system("ls *.sac > templist");
#$year = 2008;
#$day0 = 324;
#$day = 345;
#$wdir = '/auto/proj/jwalter/ant08/all/all/time/test/slips' . $tableb[$i];

#$i = 2008324;
#$max = 2008335;
#$f = 20081119;
#$fmax = 20081130;
open(TABLEB,"slipslistdec");
@tableb = <TABLEB>;
#(@dayslip,@secslip) = split ',', @tableb;
$i = 0;
while ($i < @tableb) {
	#$day = substr($i, 4, 3);
		($dayslip,$secslip) = split ',', $tableb[$i];
		$todayjd = '00032008' . $dayslip;
		$reg = ($dayslip - 336) + 1201;
		$todayreg = '00032008' . $reg;
		#stem("ls $todayjd*3.sac $todayreg*3.sac > todaylist");
		#open(TABLEC,"todaylist");
		#@tablec = <TABLEC>;
		#$f = 0;
		#while ($f < @tablec) {
		$wsuffix = '_1_noise' . ($i + 21);
		#system("$slip\n $day");
		$cut1 = $secslip - 15000;
		$cut2 = $secslip - 5000;
		print "$wsuffix";
		#open(TABLEC,"$tempsta");
		#@tempsta2 = <TABLEC>;
		#$test = transpose @tempsta2;
		#system("$cut1\n $cut2");
		#system("ls $i*3.sac $f*3.sac > stalist");
`sac << END
r $todayjd*1.sac $todayreg*1.sac
synch
w append t
cut $cut1 $cut2
r $todayjd*1.sact $todayreg*1.sact
w append $wsuffix
quit
END
`;
$i = $i + 1;
}
close(TABLEB);
