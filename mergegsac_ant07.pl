#!/usr/bin/perl -w


#open(MYFILE,">>dayslist");
#print MYFILE "$i.sac\n";
#close(MYFILE);
#system("ls *$i.sac > $i");

#$files = "/auto/proj/jwalter/ant08/all";
$put = "/auto/proj/jwalter/ant08/all/all/time/test/2007/";
$f = 20071201;
$fmax = 20071220;

while ($f < $fmax) {$i = 0;
@stalist = ('6073z2', '6073n2', '6073e2', '6127z2', '6127n2', '6127z2', '6295z2', '6295n2', '6295e2');
@astalist = ('6073_1', '6073_2', '6073_3', '6127_1', '6127_2', '6127_3', '6295_1', '6295_2', '6295_3');

while ($i < @stalist) {
	
	$loc = $put . $f . '_' . $astalist[$i] . '.sac';
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

