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
#$f = $ARGV[0];
#$fmax = $ARGV[1];
#$year = $ARGV[2];
#$files = $ARGV[3];
#$put = $ARGV[4];
#$dbname = $ARGV[5];
#$netname = $ARGV[6];

$year1=2012;
$year2=2012;
#$f=320;
#$fmax=366;
$netname = OK;
$put = "/data/okla/ContWaveform2";
$files = "/data/okla/ContWaveform";


#if (  @ARGV < 4 )
# { die ( "Usage: $0 day1 day2 " ); 
#}
#for yeari in $(gawk 'BEGIN{for(i='$year1';i<='$year2';i+=1)print i}')
#do
$yeari=$year1;
while ($yeari <= $year2) {
print "$yeari\n";
$f=1;
$fmax=60;
while ($f <= $fmax) {
$fday = sprintf("%03d",$f);
$date1=`date -d "$yeari-01-01 +$fday days -1 day" "+%Y%m%d"`;
$date = substr($date1,0,8);
print "$date\n";
#`ls -1 $files/*/*L*$fday > $put/F2`;
`ls -1 $files/$date/*SAC > $put/F2`;
#`ls -1 $files*/*/*.*.HH*$year.$fday >> $put/F2`;
#`ls -1 $files*/*/*.*.SH*$year.$fday >> $put/F2`;
#`ls -1 $files*/*/*.*.BH*$year.$fday >> $put/F2`;

#$date1=`date -d "$year-01-01 +$fday days -1 day" "+%Y%m%d"`;
#$date = substr($date1,0,8);

system("mkdir $put/$date");

open(TABLEA,"$put/F2");
@tablea = <TABLEA>;
@name = <TABLEA>;

$i = 0;
while ($i < @tablea) { 
      chomp (@tablea[$i]);
	($field1,$field2,$field3,$field4,$field5,$file1) = split '/', $tablea[$i];
	($net,$sta,$chan) = split "\\.", $file1;
	#$names = $sta . $chan . $year . $day . '.sac';
	$names = $netname . '.' . $sta . '.' . $chan . '.SAC';
	print "$names\n";
	$loc = $put . '/' . $date . '/' . $names;
	$PZfile = 'SACPZ.OK.' . $sta . '.' . $chan;
  
`sac << END
r $tablea[$i]
transfer from POLEZERO subtype $PZfile to none FREQLIMITS 0.01 0.1 15 20
rmean
bp c 3 12 n 4 p 2
interpolate delta 0.05
ch lovrok yes
w $loc.bp
quit
END
`;
#`rm $loc`;


$pts0=`saclst npts f $loc.bp`;
($blah,$pts)=split(/\s+/, $pts0);
print "$pts\n";
#if ($pts < 4300000) {
#`rm $loc.bp`;
#}
#`rm sac/*$temp`;

$i = $i + 1;
}
#$begin0=`saclst kzdate f *SAC`;
#($blah,$begin)=split(/\s+/, $begin0);
#($year,$month,$day)=split("/", $begin);
close(TABLEA);

#print "$year $month $day";
#chdir($fpath);
#`gsact $year $month $day 00 00 00 00 f $fpath/*.SAC* | gawk '{printf "r "$1"\nch o "$2"\nwh\n"} END{print "quit"}' | sac`;
#`saclst o f $fpath/*.SAC* | gawk '{printf "r %s\nch allt %.5f\nwh\n",$1,$2*(-1)} END{print "quit"}' | sac`;
#chdir($put);
$f++;
}
$yeari++;
}
#close(TABLEA);
#system("changeloc_station_cr_v2.pl");
