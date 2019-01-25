#!/usr/bin/perl -w


#open(MYFILE,">>dayslist");
#print MYFILE "$i.sac\n";
#close(MYFILE);
#system("ls *$i.sac > $i");


#$files = "/auto/proj/jwalter/ant08/all";
#$put = "/auto/proj/jwalter/green/storesac/all";
$f = 20080700;
$fmax = 20080718;



while ($f < $fmax) {$i = 0;
@stalist = ('6073e2', '6073n0', '6073n2', '6073z0', '6073z2', '6094e2', '6094n2', '6094z2', '6127e0', '6127n0', '6127z0', '6234e4', '6234n4', '6234z4');
while ($i < @stalist) {
	
	$loc = $f . '_' . $stalist[$i] . '.sac';
	#system("$stalist[$i]/$f*");
	`gsac << END
	r $stalist[$i]/$f*.sac
	merge
	w $loc
	quit
	END
	`;

$i = $i + 1;
}

$f = $f + 1;
}
