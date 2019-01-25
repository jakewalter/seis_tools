#!/usr/bin/perl -w


system("ls *sac > templist");
open(TABLEB,"templist");
@tableb = <TABLEB>;
$i = 0

while ($i < @tableb) {

`sac << END
r $tableb[$i]
taper
transfer from polezero subtype ~/bin/CMG6TDPZ_sensitive to vel freqlimits 0.001 0.005 40 45
w over
quit
END
`;
$i = $i + 1;
}

close(TABLEB);
