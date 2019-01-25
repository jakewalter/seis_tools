#!/usr/bin/perl -w

$i = 1994;
$imax = 2009;

while ($i <= $imax) {


#$put = "/auto/proj/jwalter/ant08/gsn/temp";
$f = 1;
$fmax = 30;

while ($f <= $fmax) {
$loc = $i . '.' . $f . '_VNDA_Z.sac';
$dayzeros = sprintf("%03d",$f);
print "Now making: $loc \n";
`sac << END
r $loc*v
bp c 0.012 .04 n 4 p 1
dec 5
dec 5
w append t
quit
END
`;

$f = $f + 1;
}
$i = $i +1;
}


#close(TABLEA);
