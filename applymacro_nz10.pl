#!/usr/bin/perl
@dates = <2010_0 2010_1 2010_2>;
$f = 0;
$fmax = 2;

while ($f <= $fmax) {
$datesa = $dates[$f];
`ls -1 *HE*$datesa??.sac > macros`;


#`ls -1 *HE$datesa*.sac > macros`;

open(TABLEC,"macros");
@tablec = <TABLEC>;

$i = 0;
while ($i < @tablec) { 

print $tablec[$i];

`sac << END
r $tablec[$i]
macro macrotremor2
synch
w mac$tablec[$i]
quit
END
`;
#system("rm @tablec[$i]");

$i = $i + 1;
}

system("mv mac*.sac mac");
$f = $f + 1;
}
