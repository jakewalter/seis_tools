#! /usr/bin/env perl
#-----------------------
# db2sacarrivaltime.pl
# Antelope database perl script to cut catalog data
#
# you must have perl package "Datascope.pm"
# the "use lib" line points to where antelope keeps it
#
# USAGE: db2sacarrivaltime.pl /home/jwalter9/nicoyaclean/nicclean /home/jwalter9/nicoyaquake/TempWaveform 2012-240 2012-241
# Database must contain 'origin', 'assoc', and 'arrival' tables
#  

use lib "$ENV{ANTELOPE}/data/perl/";
use Datascope;

if (  @ARGV < 2 )
 { die ( "Usage: $0 database outputdir [start] [enddate] " ); 
}

$dbname = $ARGV[0];
#$outdir = "/home/jwalter9/nicoyaquake";
$db = $ARGV[0];

$stdate= "1980-220" ; $enddate= "2099-300" ;
if ( $ARGV[1] ){ $outdir = $ARGV[1]; }
if ( $ARGV[2] ){ $stdate = $ARGV[2]; }
if ( $ARGV[3] ){ $enddate = $ARGV[3]; }
	
#open(FILEOUT, ">" , $outdir)  or die "Can't open $outdir: $!";

print "Reading database: $dbname\n";
@db = dbopen("$dbname", "r");
@dbo = dblookup(@db, "" , "origin" , "", "" );
@dbo = dbsubset(@dbo, "origin.time >= '$stdate' && origin.time <= '$enddate'");
#@dbo = dbsubset(@dbo,"orid>=12573");    #   12573
@dbo = dbsubset(@dbo, "origin.nass >= 5 ");
@dbe = @dbo;
$nrecords = dbquery(@dbo, "dbRECORD_COUNT");
$err = 0.00;
$rms = 0.00;

print "$outdir";
open(FILEOUT3, ">" , "$outdir/catalog")  or die "Can't open catalog file: $!";

#print "$nrecords";

for ( $dbe[3] = 0; $dbe[3] < $nrecords; $dbe[3]++ ) {
	$progress = $dbe[3]+1;
	print "Event number: $progress of $nrecords\n";
	
	($olat,$olon,$otime,$odepth,$omag,$orid) = dbgetv(@dbe,qw(lat lon time depth ml orid));
	print "Origin id: $orid\n";
	$odatetime = epoch2str($otime,'%Y %m %d %H %M %S.%s');
	$ostrtime = strtime($otime);
	
	$oyear = epoch2str($otime,"%Y");
	$omonth = epoch2str($otime,"%m");
	$oday = epoch2str($otime,"%d");
	$ohour = epoch2str($otime,"%H");
	$omin = epoch2str($otime,"%M");
	$osec = epoch2str($otime,"%S");
	$oall = $oyear . $omonth . $oday . $ohour . $omin;

	#print FILEOUT "# $odatetime $olat $olon $odepth $omag $err $err $rms $orid\n";
	
	@db = dbsubset(@dbo,"orid==$orid");
	@db = dbjoin(@db, dblookup(@db, "", "assoc", "" ,""));
	@db = dbjoin(@db, dblookup(@db, "", "arrival", "", ""));

	$nassoc = dbquery(@db, "dbRECORD_COUNT");
	system("mkdir $oall");

	printf FILEOUT3 "$oall $oyear $omonth $oday $ohour $omin $osec $olat $olon $odepth $omag\n";

	open(FILEOUT1, ">" , "$oall/stn.id")  or die "Can't open stn.id: $!";
	open(FILEOUT2, ">" , "$oall/wf_SNR.dat")  or die "Can't open wf_SNR.dat: $!";

##### Now for each arrival ...
	for ( $db[3] = 0; $db[3] < $nassoc; $db[3]++ ) {
		($sta, $chan, $arrtime, $deltim, $iphase) = dbgetv(@db, qw(sta chan arrival.time deltim iphase));
		
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
			`db2sac -sc $sta:$chan -ts $cstart -te $cend -gap interp -i $dbname .`;
			$phase = substr($iphase,0,1);

			#if ($phase =~ m/P/) {
			#$flag = "t1";
			#}
			#elsif ($phase =~ m/S/) {
			#$flag = "t2";
			#} 

$shift = $arrtime - $otime;
$flag = "t2";
print "$outdir/$oall/YZ.$sta.$chan.SAC.bp";
`sac << END
r sac/*$chan
rmean
bp c 5 15 n 4 p 2
synch
ch evla $olat
ch evlo $olon
ch evdp $odepth
ch o 0
ch $flag $shift
interpolate delta 0.02
w $outdir/$oall/YZ.$sta.$chan.SAC.bp
quit
END`;
printf FILEOUT1 "$sta\n";
printf FILEOUT2 "YZ.$sta.$chan.SAC.bp 10 10 1\n";

			`rm sac/*$chan`;
#			$travtim = $arrtime-$otime;
#			$phase = substr($iphase,0,1);
#			$weight = $deltim;


			#printf FILEOUT "$sta %2.3f $weight $phase\n" ,$travtim;
		#} #else
	}#for
#`saclst o f *.SAC* | gawk '{printf "r %s\nch allt %.5f\nwh\n",$1,$2*(-1)} END{print "quit"}' | sac`;
}#for
print "All files in $outdir\n"

