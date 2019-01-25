#!/usr/bin/perl -w
system("ls *.sac > batchlist");
open(TABLEB,"batchlist");
@tableb = <TABLEB>;
$i = 0;
while ($i < @tableb) {
`~/bin/hk2sac << EOF
$tableb[$i]
$tableb[$i]
EOF`;
$i++;
}
close(TABLEB);
