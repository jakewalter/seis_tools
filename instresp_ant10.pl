#!/usr/bin/perl -w


system("ls *.sac > templist");

open(TABLEB,"templist");
@tableb = <TABLEB>;
$f = 0;
while ($f < @tableb) {
#print "$table[$f] \n";
($day,$sta,$blah) = split('_', $tableb[$f]);
#($sta,$sta2) = split('\.', $sta1);
print "$sta \n";
if (($sta =~ m/S04/) || ($sta =~ m/S07/) || ($sta =~ m/S05/) || ($sta =~ m/S06/) || ($sta =~ m/S02/)) {
`sac << END
r $tableb[$f]
transfer from polezero subtype /auto/home/jwalter/bin/CMG6TDPZsensitive to vel
mul 2.1e-10
ch lovrok
w over
quit
END
`;
}
else {
`sac << END
r $tableb[$f]
transfer from polezero subtype /auto/home/jwalter/bin/3TPZ to vel
ch lovrok
w over
quit
END
`;
}
$f = $f + 1;
}
close(TABLEB)
