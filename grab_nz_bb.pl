#!/usr/bin/perl -w


#@stations = <'MXZ' 'PUZ' 'HAZ' 'URZ' 'MWZ' 'KNZ' 'BKZ' 'PXZ' 'TSZ' 'MRZ' 'BFZ' 'WEL'>;
$g = 2004;
$gmax = 2010;

while ($g <= $gmax) {
#$sta = $stations[$g]; 

$i = 1;
$imax = 12;

while ($i <= $imax) {


#$put = "/auto/proj/jwalter/ant08/gsn/temp";
$f = 1;
$fmax = 31;

while ($f <= $fmax) {
$month = sprintf("%02d",$i);
$day = sprintf("%02d",$f);
$count = $month . '_' . $day;
print "Now making: $count \n";
`java -jar ~/nz/GeoNetCWBQuery.jar -s ".......HHE." -b "$g/$month/$day 00:00:00" -d 1d -t sac -o %N_%y_%j
`;
$f = $f + 1;
}
$i = $i +1;
}
$g = $g + 1;
}


#close(TABLEA);
