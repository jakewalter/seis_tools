#!/usr/bin/perl -w
system("ls *6094*.sac > templist");
open(TABLEB,"templist");
@tableb = <TABLEB>;
$i = 0;
while ($i < @tableb) {
$wdir = '/auto/proj/jwalter/ant08/all/all/time/test/sens/' . $tableb[$i];
$newhp = '/auto/proj/jwalter/ant08/all/all/time/test/sens/' . '0003' . $tableb[$i];
#system("$newhp");
`sac << END
r $tableb[$i]
rmean
rtrend
taper
transfer from polezero subtype ../test/CMG6TDPZsensitive to vel
w $wdir
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
