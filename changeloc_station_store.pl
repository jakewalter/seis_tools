#!/usr/bin/perl -w


system("ls *.sac > templist");

open(TABLEB,"templist");
@tableb = <TABLEB>;
$f = 0;
while ($f < @tableb) {
#print "$table[$f] \n";
($day,$sta1) = split('_', $tableb[$f]);
($sta,$sta2) = split('\.', $sta1);
print "$sta \n";
if ($sta =~ m/0000e6094/) {
`sac << END
r $tableb[$f]
ch stla 70.356226
ch stlo -50.835534
ch stel 0
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/0000e6234/) {    #($sta =~ /QSPA/) {
`sac << END
r $tableb[$f]
ch stla 70.417382
ch stlo -50.616176
ch stel 0
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/0000e6127/) {
`sac << END
r $tableb[$f]
ch stla 70.401532
ch stlo -50.651662
ch stel 0
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/0000e6073/) {
`sac << END
r $tableb[$f]
ch stla 70.401532
ch stlo -50.556384
ch stel 0
w $tableb[$f]
quit
END
`;
}
$f = $f + 1;
}
close(TABLEB)
