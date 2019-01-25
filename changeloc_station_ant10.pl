#!/usr/bin/perl -w


system("ls *.sac > templist");

open(TABLEB,"templist");
@tableb = <TABLEB>;
$f = 0;
while ($f < @tableb) {
#print "$table[$f] \n";
@nums = split('\_', $tableb[$f]);
$sta = $nums[1];
print "$sta \n";
if ($sta =~ m/S01/) {
`sac << END
r $tableb[$f]
ch kstnm S01
ch stla -84.5
ch stlo -154.1
ch stel 0.0
ch lovrok
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/S02/) {
`sac << END
r $tableb[$f]
ch kstnm S02
ch stla -84.247278
ch stlo -153.575462
ch stel 0.0
ch lovrok
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/S03/) {
`sac << END
r $tableb[$f]
ch kstnm S03
ch stla -84.6
ch stlo -157.5
ch stel 0.0
ch lovrok
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/S04/) {
`sac << END
r $tableb[$f]
ch kstnm S04
ch stla -84.23
ch stlo -156.65
ch stel 0.0
ch lovrok
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/S05/) {
`sac << END
r $tableb[$f]
ch kstnm S05
ch stla -84.211987
ch stlo -158.398788
ch stel 0.0
ch lovrok
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/S06/) {
`sac << END
r $tableb[$f]
ch kstnm S06
ch stla -84.376187
ch stlo -153.964545
ch stel 0.0
ch lovrok
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/S07/) {
`sac << END
r $tableb[$f]
ch kstnm S07
ch stla -84.600064
ch stlo -154.2584948
ch stel 0.0
ch lovrok
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/S08/) {
`sac << END
r $tableb[$f]
ch kstnm S08
ch stla -84.48
ch stlo -157.7
ch stel 0.0
ch lovrok
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/S09/) {
`sac << END
r $tableb[$f]
ch kstnm S09
ch stla -84.51
ch stlo -156.1
ch stel 0.0
ch lovrok
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/S10/) {
`sac << END
r $tableb[$f]
ch kstnm S10
ch stla -84.33
ch stlo -158.125
ch stel 0.0
ch lovrok
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/S11/) {
`sac << END
r $tableb[$f]
ch kstnm S11
ch stla -84.3
ch stlo -155.5
ch stel 0.0
ch lovrok
w $tableb[$f]
quit
END
`;
}
$f = $f + 1;
}
close(TABLEB)
