#!/usr/bin/perl -w


system("ls *.SAC_deconv > templist");

open(TABLEB,"templist");
@tableb = <TABLEB>;
$f = 0;
while ($f < @tableb) {
#print "$table[$f] \n";
@nums = split('\.', $tableb[$f]);
$sta = $nums[7];
print "$sta \n";
if ($sta =~ m/ACHA/) {
`sac << END
r $tableb[$f]
ch stla 9.8278
ch stlo 85.2476
ch stel 0.1360
ch lovrok
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/ARDO/) {    #($sta =~ /QSPA/) {
`sac << END
r $tableb[$f]
ch stla 10.2136
ch stlo -85.5967
ch stel 0.1410
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/CABA/) {
`sac << END
r $tableb[$f]
ch stla 10.2362
ch stlo -85.3435
ch stel 0.0500
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/INDI/) {
`sac << END
r $tableb[$f]
ch stla 9.8650
ch stlo -85.5023
ch stel 0.1050
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/JUDI/) {
`sac << END
r $tableb[$f]
ch stla 10.1659
ch stlo -85.5383
ch stel 0.6860
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/JUDS/) {
`sac << END
r $tableb[$f]
ch stla 10.1659
ch stlo -85.5383
ch stel 0.6860
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/LEPA/) {
`sac << END
r $tableb[$f]
ch stla 9.9453
ch stlo -85.0312
ch stel 0.0150
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/MASP/) {
`sac << END
r $tableb[$f]
ch stla 10.0985
ch stlo -85.3811
ch stel 0.1030
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/PNCB/) {
`sac << END
r $tableb[$f]
ch stla 9.5894
ch stlo -85.0917
ch stel 0.0270
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/PNEG/) {
`sac << END
r $tableb[$f]
ch stla 10.1955
ch stlo -85.8291
ch stel 0.0260
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/POPE/) {
`sac << END
r $tableb[$f]
ch stla 10.0634
ch stlo -85.2633
ch stel 0.0390
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/SAJU/) {
`sac << END
r $tableb[$f]
ch stla 10.0672
ch stlo -85.7105
ch stel 0.0720
w $tableb[$f]
quit
END
`;
}
elsif ($sta =~ m/SARO/) {
`sac << END
r $tableb[$f]
ch stla 10.8430
ch stlo -85.6157
ch stel 0.3090
w $tableb[$f]
quit
END
`;
}
$f = $f + 1;
}
close(TABLEB)
