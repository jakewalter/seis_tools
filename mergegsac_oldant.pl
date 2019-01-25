#!/usr/bin/perl -w

@sta = <'6127' '6073' '6295'>;
#@stab = <'KARP' 'SALE' 'LOST' 'SAIR'>; 
$h = 0;
$hmax = 2;
while ($h <= $hmax) {


@comp = <'e' 'n' 'z'>;
$g = 0;
$gmax = 2;
while ($g <= $gmax) {

$i = 11;
$imax = 12;
while ($i <= $imax) {

$f = 1;
$fmax = 31;
while ($f <= $fmax) {
$month = sprintf("%02d",$i);
$day = sprintf("%02d",$f);
$middle = $sta[$h] . $comp[$g] . "2";
$file = "2007" . $month . $day;
$newfile = "2007" . $month . $day . "_0000" . $comp[$g] . $sta[$h] . ".sac";
#$middle = $sta[$h] . $comp[$g] . "2";
print "Now making: $newfile \n";
`gsac << END
r $middle*/$file*
rmean
merge
w new/$newfile
quit
END
`;
#system("sactosac $newfile");
`sac << END
r new/$newfile
taper
transfer from polezero subtype CMG6TDPZsensitive to vel freqlimits 0.001 0.005 40 45
w new/$newfile
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
