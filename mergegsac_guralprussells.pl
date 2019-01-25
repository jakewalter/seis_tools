#!/usr/bin/perl -w


#open(MYFILE,">>dayslist");
#print MYFILE "$i.sac\n";
#close(MYFILE);
#system("ls *$i.sac > $i");


#$files = "/auto/proj/jwalter/ant08/all";
#$put = "/auto/proj/jwalter/green/storesac/all";
$f = 20080720;
$fmax = 20080731;



while ($f < $fmax) {$i = 0;
@stalist = ('6073/6073e2', '6073/6073n0', '6073/6073n2', '6094/6094e2', '6094/6094n2', '6094/6094z2', '6127/6127e0', '6127/6127n0', '6127/6127z0');
@astalist = ('6073e2', '6073n0', '6073n2', '6094e2', '6094n2', '6094z2', '6127e0', '6127n0', '6127z0');

while ($i < @stalist) {
	
	$loc = $f . '_' . $astalist[$i] . '.sac';
        system("$stalist[$i]/$f*");
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
