#!/usr/bin/perl -w

#$i = 150;
#while ($i < 250) {
#$day=sprintf("%03d",$i);
#print "mseed/R[$i]*/*m > mseedlist";
`ls raw_data/SEall/*CN*mseed > mseedlist`;


open(TABLEB,"mseedlist");
@tableb = <TABLEB>;
$f = 0;
while ($f < @tableb) {
chomp (@tableb[$f]);
print "@tableb[$f] \n";
`miniseed2days -f -d seak -w "day_volumes/%{sta}/%{sta}.%{net}.%{loc}.%{chan}.%Y.%j" -< $tableb[$f]`;

$f = $f + 1;
}
#close(TABLEB);
#$i = $i + 1;
#}
