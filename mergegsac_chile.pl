#!/usr/bin/perl -w

$i = 2010;
@sta = <U27B U28B U41B U44B U57B U58B U59B U60B U61B U63B>;
$h = 0;
$hmax = 9;

while ($h <= $hmax) {

$f = 84;
$fmax = 365;

while ($f <= $fmax) {
$chan = HHE;
$dayzeros = sprintf("%03d",$f);
$loc = $i . '.' . $dayzeros . '.' . $sta[$h] . '.' . $chan . '.sac';
$yearday = $i . '.' . $dayzeros;
print "Now making: $dayzeros . $sta[$h] \n";
`gsac << END
r $yearday*$sta[$h]*$chan*.SAC
rmean
merge
w $loc
quit
END
`;
`sac << END
r $loc
transfer from polezero subtype SAC_PZs_XY_*$sta[$h]* to vel freqlimits 0.001 0.005 40 45
w over
quit
END
`;
$f = $f + 1;
}
$h = $h + 1;
}

#close(TABLEA);
