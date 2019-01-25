#!/usr/bin/perl -w

$i = 1994;
$imax = 2009;

while ($i <= $imax) {


#$put = "/auto/proj/jwalter/ant08/gsn/temp";
$f = 1;
$fmax = 365;

while ($f <= $fmax) {
$loc = $i . '.' . $f . '_VNDA_Z.sac';
$dayzeros = sprintf("%03d",$f);
print "Now making: $loc \n";
`gsac << END
r $i.$dayzeros*.SAC
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
transfer from evalresp to vel freqlimits 0.001 0.005 40 50
bp c 0.012 .04 n 4 p 1
abs
smooth h 50
dec 5
smooth h 50
dec 5
smooth h 50
smooth h 25
dec 5
dec 2
w over
quit
END
`;

$f = $f + 1;
}
$i = $i +1;
}


#close(TABLEA);
