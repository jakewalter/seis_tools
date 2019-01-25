#!/usr/bin/perl -w

$i = 2010;
$imax = 2011;

while ($i <= $imax) {


#$put = "/auto/proj/jwalter/ant08/gsn/temp";
$f = 1;
$fmax = 365;

while ($f <= $fmax) {
@chan = <'BHE' 'BHN' 'BHZ'>;
$g = 0;
$gmax = 2;
while ($g <= $gmax) {
$dayzeros = sprintf("%03d",$f);
$loc = $i . '.' . $dayzeros . '_MCAR_' . $chan[$g] . '.sac';
print "Now making: $loc \n";
`gsac << END
r $i.$dayzeros*$chan[$g]*.SAC
rmean
merge
w $loc
quit
END
`;
`sac << END
r $loc
transfer from polezero subtype SAC_PZs_XZ_MCAR_$chan[$g]* to vel freqlimits 0.01 0.05 40 45
w over
quit
END
`;
$g = $g + 1;
}
$f = $f + 1;
}
$i = $i + 1;
}

#close(TABLEA);
