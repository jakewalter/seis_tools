#!/usr/bin/perl -w
system("ls *.sac > templist");

open(TABLEB,"templist");
@tableb = <TABLEB>;
$f = 0;
while ($f < @tableb) {
`sac << END
r $tableb[$f]
ch lovrok true
w $tableb[$f]
quit
END
`;

$f = $f + 1;
}
close(TABLEB)

#ch lcalda true