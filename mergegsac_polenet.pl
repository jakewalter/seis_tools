#!/usr/bin/perl -w

$i = 2008;
$imax = 2010;

while ($i <= $imax) {

$f = 1;
$fmax = 365;


while ($f <= $fmax) {
@sta = <'WAIS' 'SIPL' 'PECA' 'LONW' 'HOWD' 'DUFK'>;
$h = 0;
$hmax = 5;

while ($h <= $hmax) {
@chan = <'BHE' 'BHN' 'BHZ'>;
$g = 0;
$gmax = 2;
while ($g <= $gmax) {
$dayzeros = sprintf("%03d",$f);
$loc = $i . '.' . $dayzeros . '_' . $sta[$h] . '_' . $chan[$g] . '.sac';
print "Now making: $loc \n";
`gsac << END
r $i.$dayzeros*$sta[$h]*$chan[$g]*.SAC
rmean
rtrend
taper
merge
w $loc
quit
END
`;
`sac << END
r $loc
transfer from polezero subtype SAC_PZs_YT_$sta[$h]_$chan[$g]* to vel freqlimits 0.001 0.005 30 35
w over
quit
END
`;
$g = $g + 1;
}
$h = $h + 1;
}
$f = $f + 1;
}
$i = $i + 1;
}
