#!/usr/bin/perl
@dates = <20060 20061 20062 20063 20070 20071 20072 20073 20080 20081 20082 20083 20090 20091 20092 20093>;
$f = 0;
$fmax = 16;

while ($f <= $fmax) {
$datesa = $dates[$f];
`ls -1 ?????HE$datesa*.sac > macros`;


#`ls -1 *HE$datesa*.sac > macros`;

open(TABLEC,"macros");
@tablec = <TABLEC>;

$i = 0;
while ($i < @tablec) { 

print "@tablec[$i]";

`sac << END
r @tablec[$i]
macro macrotremor2
synch
w mac@tablec[$i]
quit
END
`;
system("rm @tablec[$i]");

$i = $i + 1;
}

#system("mv mac*.sac mac");
$f = $f + 1;
}
