#!/usr/bin/perl -w
system("ls *e.sac > templista");
open(TABLEB,"templista");
@tableb = <TABLEB>;
$i = 0;
while ($i < @tableb) {
$wdir = '/auto/proj/jwalter/ant09/all/' . $tableb[$i];
$newhp = '/auto/proj/jwalter/ant09/all/' . '0003' . $tableb[$i];
$newbp = '/auto/proj/jwalter/ant09/all/a' . $tableb[$i];
#system("$newhp");
`sac << END
r $tableb[$i]
rmean
rtrend
taper
transfer from polezero subtype /auto/proj/jwalter/ant08/all/all/time/test/CMG6TDPZsensitive to vel
w $wdir
bp c .012 .04 n 4 p 1
w $newbp
quit
END
`;
`gsac << END
r $wdir
rmean
rtrend
taper
hp c .0003 n 4 p 1
w $newhp
quit
END
`;
$i = $i + 1;
}
close(TABLEB);
