#!/bin/csh
rm vertical.txt
rm horizontal*.txt
ls -d 20* > eventdirlist.txt

foreach x ( `ls -d 20*` )
echo $x
cd $x
ls ??.*.[BHE][BHN]Z.*SAC.bp > filenames1.txt
# not necessary ls ??.*.*.[HHE][HHN]Z.*SAC >> filenames1.txt
awk -F. '{print $1,$2,$3}' filenames1.txt > filenames2.txt 
sort -u filenames2.txt > filenames3.txt
#rm vertical.xy horizontal.xy
#wc -l filenames3.txt >! count.txt
foreach line ( "`cat filenames3.txt`" )
	set argv = ( $line )
	set j1 = $1
	set j2 = $2
	echo $3 > tempchannel
	set j3 = `awk '{print substr($0,0,2)}' tempchannel`
	printf "$j1 $j2 $j3\n"
	set j4 = "0"
	set weirdcomp = `ls $j1*$j2*$j3*1.*.??????.SAC.bp`
	if (-f "$weirdcomp") then
   		set j4 = 1
		printf "$j1 $j2 $j3 $j4\n"
	else
		printf "$j1 $j2 $j3 $j4\n"
	endif
	read_amplitudes.csh $j1 $j2 $j3 $j4 $x
	printf "$j1 $j2 $j3 $j4 check the files now \n"
end
cd ..
end


 
