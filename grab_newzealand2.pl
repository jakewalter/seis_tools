#!/usr/bin/perl -w

$i = 1;
$imax = 12;

while ($i <= $imax) {


#$put = "/auto/proj/jwalter/ant08/gsn/temp";
$f = 1;
$fmax = 31;

while ($f <= $fmax) {
@stations = <'MXZ' 'PUZ' 'HAZ' 'URZ' 'MWZ' 'KNZ' 'BKZ' 'PXZ' 'TSZ' 'MRZ' 'BFZ' 'WEL'>;
$g = 0;
$gmax = 12;

while ($g <= $gmax) {
$sta = $stations[$g]; 


$month = sprintf("%02d",$i);
$day = sprintf("%02d",$f);
$count = $month . '_' . $day;
print "Now making: $count \n";
`java -jar ~/nz/GeoNetCWBQuery.jar -s "..$sta..HHE." -b "2004/$month/$day 00:00:00" -d 1d -t sac -o %N_%y_%j
`;
$g = $g + 1;
}
$f = $f + 1;
}
$i = $i +1;
}


#close(TABLEA);
