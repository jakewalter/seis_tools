#!/usr/bin/perl



`ls *sac > listb`;

open(TABLEC,"listb");
@tablec = <TABLEC>;

$i = 0;
while ($i < @tablec) { 

`sac << END
r $tablec[$i]
macro macrotremor2
synch
w mac$tablec[$i]
quit
END
`;


$i = $i + 1;
}

system("mv mac*.sac mac");
close(TABLEC);
