#!/usr/bin/perl -w


#open(MYFILE,">>dayslist");
#print MYFILE "$i.sac\n";
#close(MYFILE);
#system("ls *$i.sac > $i");
#"/auto/proj/tremor/tremorDB/SEEDVOLUMES/day_volumes";

#$files = "/home/jwalter9/nicoyaclean/day_volumes";
#$put = "/home/jwalter9/nicoyaquake";
#$f = 220;
#$fmax = 300;$ARGV[3];
$f = $ARGV[0];
$fmax = $ARGV[1];
$year = $ARGV[2];
$files = $ARGV[3];
$put = $ARGV[4];
$dbname = $ARGV[5];
$netname = $ARGV[6];



if (  @ARGV < 4 )
 { die ( "Usage: $0 day1 day2 " ); 
}

while ($f <= $fmax) {
$fday = sprintf("%03d",$f);
#`ls -1 $files/*/*L*$fday > $put/F2`;
#`ls -1 $files/*/*.*.EH*$year.$fday > $put/F2`;
`ls -1 $files/day_volumes2_2013/*/*.*.HH*$year.$fday > $put/F2`;
`ls -1 $files/day_volumes2_2014/*/*.*.HH*$year.$fday >> $put/F2`;
`ls -1 $files/day_volumes2_2015/*/*.*.HH*$year.$fday >> $put/F2`;
#`ls -1 $files/*/*.*.SH*$year.$fday >> $put/F2`;
#`ls -1 $files/*/*.*.BH*$year.$fday >> $put/F2`;

$date1=`date -d "$year-01-01 +$fday days -1 day" "+%Y%m%d"`;
$date = substr($date1,0,8);

system("mkdir $put/$date");

open(TABLEA,"$put/F2");
@tablea = <TABLEA>;
@name = <TABLEA>;

$i = 0;
while ($i < @tablea) { 
      chomp (@tablea[$i]);
	($field1,$field2,$field3,$field4,$field5,$field6,$sta,$file1) = split '/', $tablea[$i];
	($field1,$field2,$field3,$chan,$year,$day) = split "\\.", $file1;
	#$names = $sta . $chan . $year . $day . '.sac';
	$names = $netname . '.' . $sta . '.' . $chan . '.SAC';
	#print "$names\n";
	$loc = $put . '/' . $date . '/' . $names;
	#$fpath = $put . '/' . $fput;
	#chdir $sta;

	$cstart = $year . ':' . sprintf("%03d",$day) . ':00:00:00.000';
	$cend = $year . ':' . sprintf("%03d",$day+1) . ':00:00:00.000';
	if ($sta =~ m/WMOK/) {
	$chan = $chan . '_00';}
	elsif ($sta =~ m/HG00/) { 
	$chan = $chan . '_A';}
	elsif ($chan =~ m/AZDA/) { 
	$chan = $chan . '_00';}
	elsif ($chan =~ m/EML1/) { 
	$chan = $chan . '_00';}
	elsif ($chan =~ m/FNO/) { 
	$chan = $chan . '_01';}
	elsif ($chan =~ m/IFCF/) { 
	$chan = $chan . '_00';}
	elsif ($chan =~ m/IFDF/) { 
	$chan = $chan . '_00';}
	elsif ($sta =~ m/NATX/) { 
	$chan = $chan . '_00';}
	elsif ($chan =~ m/OK026/) { 
	$chan = $chan . '_00';}
	elsif ($chan =~ m/V2600/) { 
	$chan = $chan . '_00';}	
	elsif ($chan =~ m/VBB1/) { 
	$chan = $chan . '_00';}
	elsif ($chan =~ m/VBMH/) { 
	$chan = $chan . '_00';}	
	elsif ($chan =~ m/VMCM/) { 
	$chan = $chan . '_00';}
	elsif ($chan =~ m/VNLC/) { 
	$chan = $chan . '_00';}	
	elsif ($chan =~ m/VPCK/) { 
	$chan = $chan . '_00';}
	elsif ($chan =~ m/VSAB/) { 
	$chan = $chan . '_00';}	
	elsif ($chan =~ m/NATX/) { 
	$chan = $chan . '_00';}
	
#	if ($chan =~ m/BH1_00/) {
#        $chan = 'BHN_00';}
#	if ($chan =~ m/BH2_00/) {
        
#$chan = 'BHE_00';}



print "$loc check thissssssssssssssssssssssssss";
	`db2sac -sc $sta:$chan -ts $cstart -te $cend -gap interp -i $dbname .`;
	#`db2sac -sc $stachan2 -ts $jstart -te $jend -gap interp -i $dbname .`;
	$temp = $sta . '.' . $chan;
	print "$loc $cstart $cend $temp\n";
	print "$chan\n";
	#system("ms2sac -G 100000 $tablea[$i] > $loc");
#	system("mkdir $put/$fday");
#chdir $files;
`gsac << END
r sac/*$temp
merge
w $loc
ch lovrok t
quit
END
`;
#`sac << END
#r $loc.bp
#rmean
#bp c 4 10 n 4 p 2
#interpolate delta 0.05
#ch lovrok yes
#w $loc.bp
#quit
#END
#`;
#`rm $loc`;


$pts0=`saclst npts f $loc.bp`;
($blah,$pts)=split(/\s+/, $pts0);
print "$pts\n";
#if ($pts < 4300000) {
#`rm $loc.bp`;
#}
`rm sac/*$temp`;

$i = $i + 1;
}
#$begin0=`saclst kzdate f *SAC`;
#($blah,$begin)=split(/\s+/, $begin0);
#($year,$month,$day)=split("/", $begin);


#print "$year $month $day";
#chdir($fpath);
#`gsact $year $month $day 00 00 00 00 f $fpath/*.SAC* | gawk '{printf "r "$1"\nch o "$2"\nwh\n"} END{print "quit"}' | sac`;
#`saclst o f $fpath/*.SAC* | gawk '{printf "r %s\nch allt %.5f\nwh\n",$1,$2*(-1)} END{print "quit"}' | sac`;
#chdir($put);
$f++;
}

close(TABLEA);
#system("changeloc_station_cr_v2.pl");
