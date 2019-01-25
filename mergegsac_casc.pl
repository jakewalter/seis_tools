#!/usr/bin/perl -w

@sta = <'6127' '6234' '6073' '6094'>;
@stab = <'KARP' 'SALE' 'LOST' 'SAIR'>; 
$h = 0;
$hmax = 3;
while ($h <= $hmax) {


@comp = <'e' 'n' 'z'>;
$g = 0;
$gmax = 2;
while ($g <= $gmax) {

$i = 7;
$imax = 9;
while ($i <= $imax) {

$f = 1;
$fmax = 31;
while ($f <= $fmax) {
$month = sprintf("%02d",$i);
$day = sprintf("%02d",$f);
$file = "2010" . $month . $day . "_0000" . $comp[$g];
$newfile = "2010" . $month . $day . "_0000" . $comp[$g] . $stab[$h] . $sta[$h] . ".sac";
$middle = $sta[$h] . $comp[$g] . "4";

print "Now making: $newfile \n";
`gsac << END
r $stab[$h]/*$middle*/$file*
rmean
merge
w $newfile
quit
END
`;
#system("sactosac $newfile");
#`sac << END
#r $newfile
#taper
#transfer from polezero subtype CMG6TDPZ_sensitive to vel freqlimits 0.001 0.005 40 45
#w $newfile
#quit
#END
#`;
$f = $f + 1;
}
$i = $i + 1;
}
$g = $g + 1;
}
$h = $h + 1;
}