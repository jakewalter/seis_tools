#!/usr/bin/perl -w

system("ls *A*1.sac > templistbp");
open(TABLEB,"templistbp");
@tableb = <TABLEB>;
$i = 0;
while ($i < @tableb) {
`sac << END
r $tableb[$i]
bp c .012 .04 n 4 p 1
synch
w append _a
quit
END
`;
$i = $i +1;
}


close(TABLEB);
