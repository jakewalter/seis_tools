#!/usr/bin/perl -w


`ls *mseed > F2`;
open(TABLEA,"F2");
@tablea = <TABLEA>;
$i = 0;
while ($i < @tablea) {
chomp(@tablea[$i]);
$tempa = $tablea[$i];
#$tempa = "CLRK.YT.mseed";
$day = 339;
$daymax = 339;
$year = 2008;
$yearmax = 2008;

while ($year <= $yearmax) {
 
while ($day <= $daymax) { 
$daynext = $day + 1;
$starttime = $year . "," . sprintf("%03d",$day) . ",00.00:00.0000";
$endtime = $year . "," . sprintf("%03d",$daynext) . ",00.00:00.0000";
print("$day" . "_$tempa\n");
`rdseed << END
$tempa

1
d





1
n



$starttime
$endtime

Y
quit
END
`;
print ("$tempa");
$day = $day +1;
};
system("rm rdseed.err_log");
$year = $year+1;
};
$i++;
}
