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
$f = 1;
$fmax = 250;
$df = 0.5;  #
#$dlength = 0.25;  #coarse duration
$dlength = 1;
$files ='/disk/cg5/jwalter/dallas/longercross/day_volumes';
$put = '/disk/cg5/jwalter/dallas/longercross/ContWaveform';
$dbname = '/disk/staff/jwalter/mendenhall/mend12';
$netname = 'YY';
$sta = 'WINT_';
$tempsta = 'WINT';
#PORT_
$chan = 'HHZ';


#if (  @ARGV < 4 )
# { die ( "Usage: $0 day1 day2 " ); 
#}

while ($f <= $fmax) {
#$fday = sprintf("%03d",$f);

#$date1=`date -d "2012-01-01 +$fday days -1 day" "+%Y%m%d"`;
#$date = substr($date1,0,8);

$fdayeven = sprintf("%03d",$f);
$fdayremain = $f - $fdayeven;
$fhours = $fdayremain*24;
$fadd = $dlength*24;
$fhours2 = $fhours + $fadd;
#print "$f $fdayeven $fdayremain $fhours\n\n\n";
#$fdaynow = $fday +$f;
$fdaynow2 = $fdayeven + $dlength;
#	($field1,$field2,$field3,$chan,$year,$day) = split "\\.", $file1;
$datename = `date -d "2012-01-01 +$fdayeven days +$fhours hours -1 day" "+%Y%j%H%M"`;
#$datename = `echo "$datename" | gawk '{$1=$1}1'`;
$datename =~ s/\s+$//;
print "$datename\n";
$names = $datename . '.' . $sta . '.' . $chan .  '.SAC';
	#print "$names\n";
$loc = $put . '/' . $names;
	#$fpath = $put . '/' . $fput;
	#chdir $sta;
	#date -d "2012-01-01 +200 days -1 day" "+%Y/%m/%d %H:%M:%S";
#$fdaynow = $fday + $f;
#$fdaynow2 = $fday + $f + $dlength;
$jstart = `date -d "2012-01-01 +$fdayeven days +$fhours hours -1 day" "+%Y:%j:%H:%M:%S"`;
$jstart =~ s/\s+$//;
$jend = `date -d "2012-01-01 +$fdayeven days +$fhours2 hours -1 day" "+%Y:%j:%H:%M:%S"`;
$jend =~ s/\s+$//;
unless(`db2sac -sc $sta:$chan -ts $jstart -te $jend -gap interp -i $dbname .`) {
`db2sac -sc $sta:$chan*_00 -ts $jstart -te $jend -gap interp -i $dbname .`};
$temp = $sta . '.' . $chan;
print "$loc $jstart $jend $f\n";
	#system("ms2sac -G 100000 $tablea[$i] > $loc");
#	system("mkdir $put/$fday");
#chdir $files;
`gsac << END
r sac/*$temp
merge
rmean
w $loc.bp
quit
END
`;
`rm sac/*$temp`;
$f = $f + $df;
};
