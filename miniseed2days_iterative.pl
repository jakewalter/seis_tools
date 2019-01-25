#!/usr/bin/perl -w

$i = 31;
while ($i < 37) {
#print "mseed/R[$i]*/*m > mseedlist";
`ls mseed/R$i*/*m > mseedlist`;

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
