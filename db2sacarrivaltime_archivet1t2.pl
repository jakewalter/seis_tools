#! /usr/bin/env perl
#-----------------------
# db2sacarrivaltime.pl
# Antelope database perl script to cut catalog data
#
# you must have perl package "Datascope.pm"
# the "use lib" line points to where antelope keeps it
#
# USAGE: db2sacarrivaltime.pl /home/jwalter9/nicoyaclean/nicclean /home/jwalter9/nicoyaquake 2012-240 2012-241
# Database must contain 'origin', 'assoc', and 'arrival' tables
#  

use lib "$ENV{ANTELOPE}/data/perl/";
use Datascope;

if (  @ARGV < 2 )
 { die ( "Usage: $0 database outputdir [start] [enddate] " ); 
}

$dbname = $ARGV[0];
$outdir = "/home/jwalter9/nicoyaquake";
$db = $ARGV[0];

$stdate= "2012-220" ; $enddate= "2012-300" ;
if ( $ARGV[2] ){ $outdir = $ARGV[1]; }
if ( $ARGV[2] ){ $stdate = $ARGV[2]; }
if ( $ARGV[3] ){ $enddate = $ARGV[3]; }
	
#open(FILEOUT, ">" , $outdir)  or die "Can't open $outdir: $!";

print "Reading database: $dbname\n";
@db = dbopen("$dbname", "r");
@dbo = dblookup(@db, "" , "origin" , "", "" );
@dbo = dbsubset(@dbo, "origin.time >= '$stdate' && origin.time <= '$enddate'");
@dbe = @dbo;
$nrecords = dbquery(@dbo, "dbRECORD_COUNT");
$err = 0.00;
$rms = 0.00;

#print "$nrecords";

for ( $dbe[3] = 0; $dbe[3] < $nrecords; $dbe[3]++ ) {
	$progress = $dbe[3]+1;
	print "Event number: $progress of $nrecords\n";
	($olat,$olon,$otime,$odepth,$omag,$orid) = dbgetv(@dbe,qw(lat lon time depth mb orid));
	$odatetime = epoch2str($otime,'%Y %m %d %H %M %S.%s');
	$ostrtime = strtime($otime);
	
	$oyear = epoch2str($otime,"%Y");
	$omonth = epoch2str($otime,"%m");
	$oday = epoch2str($otime,"%d");
	$ohour = epoch2str($otime,"%H");
	$omin = epoch2str($otime,"%M");
	$oall = $oyear . $omonth . $oday . $ohour . $omin;

	#print FILEOUT "# $odatetime $olat $olon $odepth $omag $err $err $rms $orid\n";
	
	@db = dbsubset(@dbo,"orid==$orid");
	@db = dbjoin(@db, dblookup(@db, "", "assoc", "" ,""));
	@db = dbjoin(@db, dblookup(@db, "", "arrival", "", ""));

	$nassoc = dbquery(@db, "dbRECORD_COUNT");
	system("mkdir $oall");
##### Now for each arrival ...
	for ( $db[3] = 0; $db[3] < $nassoc; $db[3]++ ) {
		($sta, $chan, $arrtime, $deltim, $iphase) = dbgetv(@db, qw(sta chan arrival.time deltim iphase));
		
		# If we want to remove certain stations
		#if ($sta =~ /TAKO/ || $sta =~ /MEGW/) {
		#	print "Removed sta $sta from event $orid.\n";}
		#else {
			
			##### cut 5 sec and 10 after arrival time at station
			$cut0 = $otime;
			$cut1 = $otime + 60;
			$cyear = epoch2str($cut0,"%Y");
			$cmonth = epoch2str($cut0,"%m");
			$cday = epoch2str($cut0,"%d");
			$chour = epoch2str($cut0,"%H");
			
			$cmin0 = epoch2str($cut0,"%M");
			$csec0 = epoch2str($cut0,"%S.%s");
			$cmin1 = epoch2str($cut1,"%M");
			$csec1 = epoch2str($cut1,"%S.%s");

			$datej=`date -d "$cyear/$cmonth/$cday" +%j`;
			$cstart = $cyear . ':' . sprintf("%03d",$datej) . ':' . $chour . ':' . $cmin0 . ':' . $csec0;
			$cend = $cyear . ':' . sprintf("%03d",$datej) . ':' . $chour . ':' . $cmin1 . ':' . $csec1;
			
			#$date1=`date -d "$year1-01-01 +$j days -1 day" "+%Y/%m/%d"`;    ### convert from DOY to Y/m/d

			##########db2sac -sc T14A:BH* -ts 2007:146:23:45:23 -te 2007:146:23:50:23 /home/jwalter9/nicoyaclean/nicclean $outdir/ContWaveform
			`db2sac -sc $sta:$chan -ts $cstart -te $cend /home/jwalter9/nicoyaclean/nicclean .`;
			$phase = substr($iphase,0,1);

			if ($phase =~ m/P/) {
			$flag = "t1";
			}
			elsif ($phase =~ m/S/) {
			$flag = "t2";
			} 
			$shift = $arrtime - $otime;
			
print "$shift";
`sac << END
r sac/*$chan
bp c 5 15 n 4 p 2
w temp
r temp
synch
ch evla $olat
ch evlo $olon
ch evdp $odepth
ch o 0
ch $flag $shift
interpolate delta 0.01
w $outdir/$oall/YZ.$sta.$chan.SAC
w $outdir/$oall/YZ.$sta.$chan.SAC.bp
quit
END`;


			`rm sac/*$chan`;
			$travtim = $arrtime-$otime;
			$phase = substr($iphase,0,1);
			$weight = $deltim;


			#printf FILEOUT "$sta %2.3f $weight $phase\n" ,$travtim;
		#} #else
	}#for
#`saclst o f *.SAC* | gawk '{printf "r %s\nch allt %.5f\nwh\n",$1,$2*(-1)} END{print "quit"}' | sac`;
}#for
print "Done: $outdir\n"

