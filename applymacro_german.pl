#!/usr/bin/perl
@dates = <200713 200714>;
$f = 0;
$fmax = 2;

while ($f <= $fmax) {



`ls -1 *e*$dates[$f]*.sac > macros`;

open(TABLEB,"macros");
@tableb = <TABLEB>;

$i = 0;
while ($i < @tableb) { 

system("@tableb[$i]");

`sac << END
r @tableb[$i]
macro macrotremor2
synch
w mac@tableb[$i]
quit
END
`;


$i = $i + 1;
}

system("mv mac*.sac mac/test");
$f++;
}
