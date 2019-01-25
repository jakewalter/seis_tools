#!/usr/bin/perl -w


system("ls *.sac > templist");

open(TABLEB,"templist");
@tableb = <TABLEB>;
$f = 0;
while ($f < @tableb) {

print "$tableb[$f] \n";

`gsac << END
r $tableb[$f]
bp c .005 .1 n 4 p 1
w $tableb[$f]
quit
END
`;
`sac << END
r $tableb[$f]
dec 4
dec 5
w $tableb[$f]
quit
END
`;
#system("rm $tableb]$f]");
$f = $f + 1;
}
close(TABLEB)
