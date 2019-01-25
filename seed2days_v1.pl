#!/usr/bin/perl -w

#$i = 1;
#while ($i < 240) {
#$day=sprintf("%03d",$i);
#print "mseed/R[$i]*/*m > mseedlist";
`ls /disk/staff/jwalter/southeastAK/raw_data_cnsn/HG_CNSN/*/*/* > seedlist`;
#`ls mseed/*/*.m*d >> mseedlist`;
#`ls mseed/*/*/*.m*d >> mseedlist`;
#print "$day \n";
open(TABLEB,"seedlist");
@tableb = <TABLEB>;
$f = 0;
while ($f < @tableb) {
chomp (@tableb[$f]);
print "@tableb[$f] \n";
`seed2db $tableb[$f] seak2`;

$f = $f + 1;
}
close(TABLEB);
#$i = $i + 1;
#}
