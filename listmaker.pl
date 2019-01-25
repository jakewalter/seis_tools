#!/usr/bin/perl
@dates = <2006 2007 2008 2009>;
$f = 0;
$fmax = 4;

while ($f <= $fmax) {

$i = 001;
$max = 365;
while ($i <= $max) {
$num = $dates[$f] . sprintf("%03d",$i);
#open(MYFILE,">>dayslist");
#print MYFILE "$i.sac\n";
#close(MYFILE);
system("ls *E$num.sac > $num");
$i++;
}
$f++;
}
