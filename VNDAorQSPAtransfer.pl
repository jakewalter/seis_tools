#!/usr/bin/perl


$i = 2008325;
$max = 2008344;
while ($i <= $max) {
print "$i\n";
`sac << END
r $i*VNDA*.sac
transfer from evalresp to vel
w over
quit
END
`;
`sac << END
r $i*QSPA*.sac
transfer from evalresp to vel
w over
quit
END
`;
$i++;
}

