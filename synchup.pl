#!/usr/bin/perl

$i = 0;
$imax = 365;
$year = 2008;
while ($i < $imax) { 
$aft = $year . sprintf("%03d",$i);
print "Synching: $aft\n";
`sac << END
r mac*HE*$aft.sac
synch
w over
quit
END
`;


$i = $i + 1;
}
