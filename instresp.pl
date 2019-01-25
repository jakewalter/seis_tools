#!/usr/bin/perl
`ls -1 *.sac > templist`;
open(TABLEA,"templist");
@tablea = <TABLEA>;


$i = 0;
while ($i < @tablea) { 

`sac << END
r $tablea[$i]
rtrend
transfer from polezero subtype CMG6TDPZ to none freqlimit .004 .02 40 50
synch
w $tablea[$i]
quit
END
`;

$i++;
}


