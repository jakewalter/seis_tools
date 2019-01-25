#!/usr/bin/perl
@dates = <20081 20082 20083>;
$f = 0;
$fmax = 10;

while ($f <= $fmax) {



`ls -1 *HE$dates[$f]*.sac > macros1`;

open(TABLED,"macros1");
@tabled = <TABLED>;

$i = 0;
while ($i < @tabled) {

system("@tableb[$i]");

`sac << END
r @tabled[$i]
macro macrotremor
synch
w mac@tabled[$i]
quit
END
`;


$i = $i + 1;
}

system("mv mac*.sac mac");
$f++;
}
close(TABLED)
