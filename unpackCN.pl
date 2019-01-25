#!/usr/bin/perl -w

#$i = 150;
#while ($i < 250) {
#$day=sprintf("%03d",$i);
#print "mseed/R[$i]*/*m > mseedlist";
`ls CN*tar > tarlist`;
`export ALT_RESPONSE_FILE=blah`;


open(TABLEB,"tarlist");
@tableb = <TABLEB>;
$f = 0;
while ($f < @tableb) {
chomp (@tableb[$f]);
print "$tableb[$f] \n";

#($dir1, $dir2,$file1) = split '/', $tableb[$f];
#print "$file1\n";

`tar -xvf $tableb[$f]`;
($net,$sta) = split "\\_", $tableb[$f];
$mseedname = $sta . '.' . $net . '2.mseed';

`rdseed -d -f DATA.*CNDC -o 4`;
`rm DATA.*CNDC`;
`cp mini.seed $mseedname`;
`rm mini.seed`;
print "$mseedname\n";

`miniseed2days -d ../../seak -w "../../day_volumes/%{sta}/%{sta}.%{net}.%{loc}.%{chan}.%Y.%j" -< $mseedname`;

$f = $f + 1;
}
close(TABLEB);
#$i = $i + 1;
#}
