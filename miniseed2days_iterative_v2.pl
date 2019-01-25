#!/usr/bin/perl -w

$i = 1;
while ($i < 240) {
$day=sprintf("%03d",$i);
#print "mseed/R[$i]*/*m > mseedlist";
`ls ref_ucsc_early2012/*/2012.$day*m > mseedlist`;
#`ls mseed/*/*.m*d >> mseedlist`;
#`ls mseed/*/*/*.m*d >> mseedlist`;
print "$day \n";
open(TABLEB,"mseedlist");
@tableb = <TABLEB>;
$f = 0;
while ($f < @tableb) {
chomp (@tableb[$f]);
print "@tableb[$f] \n";
`miniseed2days -d nicclean -w "day_volumes/%{sta}/%{sta}.%{net}.%{loc}.%{chan}.%Y.%j" -< $tableb[$f]`;

$f = $f + 1;
}
close(TABLEB);
$i = $i + 1;
}
