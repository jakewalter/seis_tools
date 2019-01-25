#!/usr/bin/perl


$i = 001;
$max = 365;
while ($i <= $max) {
@num = $i;
#open(MYFILE,">>dayslist");
#print MYFILE "$i.sac\n";
#close(MYFILE);
$num = sprintf("%03d",$i);
system("ls *BFZ__HH*2005_$num > $i");
system("ls *BKZ__HH*2005_$num >> $i");
system("ls *KNZ__HH*2005_$num >> $i");
system("ls *MRZ__HH*2005_$num >> $i");
system("ls *MWZ__HH*2005_$num >> $i");
system("ls *MXZ__HH*2005_$num >> $i");
system("ls *PUZ__HH*2005_$num >> $i");
system("ls *PXZ__HH*2005_$num >> $i");
system("ls *TSZ__HH*2005_$num >> $i");
system("ls *WEL__HH*2005_$num >> $i");
$i++;
}
