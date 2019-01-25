#!/usr/bin/perl -w

$i = 2007;
$imax = 2011;

while ($i <= $imax) {

#$put = "/auto/proj/jwalter/ant08/gsn/temp";
$f = 1;
$fmax = 365;

while ($f <= $fmax) {
$loc = $i . '.' . sprintf("%03d",$f) . '_QSPA_Z.sac';
$dayzeros = sprintf("%03d",$f);
print "Now making: $loc \n";
`gsac << END
r $i.$dayzeros*BHZ*.SAC
merge
w $loc
quit
END
`;
`sac << END
r $loc
ch lovrok
transfer from evalresp to vel freqlimits 0.001 0.005 40 50
bp c .02 .05 n 4 p 2
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
