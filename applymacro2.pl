#!/usr/bin/perl
@dates = <20070 20071 20072 20073>;
$f = 0;
$fmax = 10;

while ($f <= $fmax) {



`ls -1 *HE*$dates[$f]*.sac > macros`;

open(TABLEB,"macros");
@tableb = <TABLEB>;

$i = 0;
while ($i < @tableb) { 

system("@tableb[$i]");

`sac << END
r @tableb[$i]
macro macrotremor2
synch
w macf@tableb[$i]
quit
END
`;


$i = $i + 1;
}

system("mv macf*.sac mac/full");
$f++;
}
