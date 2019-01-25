#!/usr/bin/perl

`ls *.sac > macros`;

open(TABLEC,"macros");
@tablec = <TABLEC>;

$i = 0;
while ($i < @tablec) { 
($day,$sta,$sta2,$chan) = split '_', $tablec[$i];
print "Making: @tablec[$i]\n";

if ($sta == 9900) {
`sac << END
r @tablec[$i]
dec 2
w over
END
`;
}
elsif ($sta =~ /a702/) {
`sac << END
r @tablec[$i]
dec 2
w over
END
`;
}

`sac << END
r @tablec[$i]
bp c .012 .04 n 4 p 2
abs
smooth h 50
dec 5
smooth h 50
dec 5
smooth h 50
synch
w over
quit
END
`;


$i = $i + 1;
}
