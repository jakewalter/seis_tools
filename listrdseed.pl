#!/usr/bin/perl


$i = 1;
$max = 23;
while ($i <= $max) {
@num = $i;
#open(MYFILE,">>dayslist");
#print MYFILE "$i.sac\n";
#close(MYFILE);
system("rdseed -d -f AntVNDA_1994_2009all.$i*");
$i++;
}
