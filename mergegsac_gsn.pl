#!/usr/bin/perl -w

@sta = <AAK CMLA KIV PFO ABKT COCO KURK RPN ABPO DGAR KWAJ RPN ABPO DGAR LVZ SUR ALE ERM NIL SUR ALE ESK NIL TAU ARU FFC NNA TLY BFO HOPE NNA WRAB BORG KAPI OBN WRAB BRVK KDAK OBN XPFO CMLA KIV PFO XPFO>;
$h = 0;
$hmax = 43;

while ($h <= $hmax) {


$i = 2007;
$imax = 2007;

while ($i <= $imax) {


#$put = "/auto/proj/jwalter/ant08/gsn/temp";
$f = 346;
$fmax = 346;

while ($f <= $fmax) {
@chan = <'BHZ' 'BHE' 'BHN'>;
$g = 0;
$gmax = 0;
while ($g <= $gmax) {
$dayzeros = sprintf("%03d",$f);
$loc = $i . '.' . $dayzeros . '.' . $sta[$h] . $chan[$g] . '.sac';
#print "Now making: $sta[$h] \n";
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
transfer from polezero subtype SAC_PZs_XZ_$sta[$h]_$chan[$g]* to vel freqlimits 0.001 0.005 40 45
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
