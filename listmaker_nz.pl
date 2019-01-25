#!/usr/bin/perl


$i = 001;
$max = 365;
while ($i <= $max) {
@num = $i;
#open(MYFILE,">>dayslist");
#print MYFILE "$i.sac\n";
#close(MYFILE);
$num = sprintf("%03d",$i);
system("ls *2010_$num.sac > 2010$num");
$i++;
}
