#!/usr/bin/perl -w

@sta = <'6234' '6073' '6094' '6127'>;
#@stab = <'KARP' 'SALE' 'LOST' 'SAIR'>; 
$h = 0;
$hmax = 3;
while ($h <= $hmax) {


@comp = <'e' 'n' 'z'>;
$g = 0;
$gmax = 2;
while ($g <= $gmax) {

$i = 5;
$imax = 7;
while ($i <= $imax) {

$f = 1;
$fmax = 31;
while ($f <= $fmax) {
$month = sprintf("%02d",$i);
$day = sprintf("%02d",$f);
$file = "2008" . $month . $day . "_????.sac";
$newfile = "2008" . $month . $day . "_0000" . $comp[$g] . $sta[$h] . ".sac";
$middle = $sta[$h] . $comp[$g];

print "Now making: $newfile \n";
`gsac << END
r ../*$middle*/$file*
merge
w $newfile
quit
END
`;
#system("sactosac $newfile");
`sac << END
r $newfile
transfer from polezero subtype /auto/home/jwalter/bin/CMG6TDPZsensitive to vel
mul 2.1e-10
w over
quit
END
`;
$f = $f + 1;
}
$i = $i + 1;
}
$g = $g + 1;
}
$h = $h + 1;
}
