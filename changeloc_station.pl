#!/usr/bin/perl -w


system("ls *.sac*slip* > templista");

open(TABLEB,"templista");
@tableb = <TABLEB>;
$f = 0;
while ($f < @tableb) {
($day,$sta,$sta2,$chan) = split '_', $tableb[$f];
if ($sta == 6234) {
`sac << END
r $tableb[$f]
ch lovrok true
ch evla -84.2
ch evlo -158
ch stla -84.4691
ch stlo -152.0599
ch stel 0
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ /QSPA/) {
`sac << END
r $tableb[$f]
ch lovrok true
ch evla -84.2
ch evlo -158
ch stla -90
ch stlo -155
ch stel 0
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ /VNDA/) {
`sac << END
r $tableb[$f]
ch lovrok true
ch evla -84.2
ch evlo -158
ch stla -77.5172
ch stlo -161.8528
ch stel 0
w $tableb[$f]
quit
END
`;
}
elsif ($sta == 9900) {
`sac << END
r $tableb[$f]
ch lovrok true
ch evla -84.2
ch evlo -158
ch stla -84.3763
ch stlo -153.9782
ch stel 0
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ /a702/) {
`sac << END
r $tableb[$f]
ch lovrok true
ch evla -84.2
ch evlo -158
ch stla -84.3789
ch stlo -158.8525
ch stel 0
w $tableb[$f]
quit
END
`;
}
elsif ($sta == 6127) {
`sac << END
r $tableb[$f]
ch lovrok true
ch evla -84.2
ch evlo -158
ch stla -84.2473
ch stlo -153.5738
ch stel 0
w $tableb[$f]
quit
END
`;
}
elsif ($sta == 6094) {
`sac << END
r $tableb[$f]
ch lovrok true
ch evla -84.2
ch evlo -158
ch stla -84.5753
ch stlo -152.7644
ch stel 0
w $tableb[$f]
quit
END
`;
}
$f = $f + 1;
}
close(TABLEB)
