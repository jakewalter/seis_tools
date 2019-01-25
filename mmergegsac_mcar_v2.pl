#!/usr/bin/perl -w


@sta = <'BARN' 'PTPK'>;

$h = 0;
$hmax = 1;

while ($h <= $hmax) {

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
$loc = $i . '.' . $dayzeros . '_' . $sta[$h] . '_' . $chan[$g] . '.sac';
print "Now making: $loc \n";
`gsac << END
r $i.$dayzeros*$sta[$h]*$chan[$g]*.SAC
rmean
merge
w $loc
quit
END
`;
`sac << END
r $loc
transfer from polezero subtype SAC_PZs_XZ_$sta[$h]_$chan[$g]* to vel freqlimits 0.01 0.05 40 45
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
$h = $h + 1;
}

#close(TABLEA);
