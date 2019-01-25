#!/usr/bin/perl

$year = 2004;
$yearmax = 2010;
while ($year <= $yearmax) {
$i = 001;
$max = 365;
while ($i <= $max) {
@num = $i;
#open(MYFILE,">>dayslist");
#print MYFILE "$i.sac\n";
#close(MYFILE);
$num = sprintf("%03d",$i);
$listname = $year . $num;
system("ls *BFZ__HHE*$year*_*$num > $listname");
system("ls *BKZ__HHE*$year*_*$num >> $listname");
system("ls *KNZ__HHE*$year*_*$num >> $listname");
system("ls *MRZ__HHE*$year*_*$num >> $listname");
system("ls *MWZ__HHE*$year*_*$num >> $listname");
system("ls *MXZ__HHE*$year*_*$num >> $listname");
system("ls *PXZ__HHE*$year*_*$num >> $listname");
system("ls *TSZ__HHE*$year*_*$num >> $listname");
system("ls *PUZ__HHE*$year*_*$num >> $listname");
system("ls *HAZ__HHE*$year*_*$num >> $listname");
system("ls *URZ__HHE*$year*_*$num >> $listname");
system("ls *WEL__HHE*$year*_*$num >> $listname");
$i++;
}
$year++;
}
