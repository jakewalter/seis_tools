#! /usr/bin/env perl
#-----------------------
# db_mkHypoDD.pl    -MCW
# Antelope database perl script
#
# Produces a "phase.dat"-style pickfile for hypoDD
# from an Antelope CSS 3.0 database
#
# you must have perl package "Datascope.pm"
# the "use lib" line points to where antelope keeps it
#
# USAGE: db_mkHypoDD.pl my_database
# Database must contain 'origin', 'assoc', and 'arrival' tables
# OUTPUT: file "hdd_picks.dat" 

use lib "$ENV{ANTELOPE}/data/perl/";
use Datascope;

if (  @ARGV < 1 )
 { die ( "Usage: $0 database [outputfile] [start] [enddate]" ); 
}
$outfile = hypoddpicks.pha;
$stdate= "1980-220" ; $enddate= "2099-300" ;
if ( $ARGV[1] ){ $outfile = $ARGV[1]; }
if ( $ARGV[2] ){ $stdate = $ARGV[2]; }
if ( $ARGV[3] ){ $enddate = $ARGV[3]; }




$dbname = $ARGV[0];
#$outfile = "hdd_picks.dat";
open(FILEOUT, ">" , $outfile)  or die "Can't open $outfile: $!";

print "Reading database: $dbname\n";
@db = dbopen("$dbname", "r");
@dbo = dblookup(@db, "" , "origin" , "", "" );
@dbo = dbsubset(@dbo, "origin.time >= '$stdate' && origin.time <= '$enddate'");
#@dbo = dbsubset(@dbo, "origin.nass >= 10 ");
#@dbo = dbsubset(@dbo, "origin.lat >= 32 ");
#@dbo = dbsubset(@dbo, "origin.lat <= 33 ");
#@dbo = dbsubset(@dbo, "origin.lon <= -93 ");
#@dbo = dbsubset(@dbo, "origin.lon >= -94 ");
@dbe = @dbo;
$nrecords = dbquery(@dbo, "dbRECORD_COUNT");
$err = 0.000;
$rms = 0.00;
$dbtimeprev=0;

for ( $dbe[3] = 0; $dbe[3] < $nrecords; $dbe[3]++ ) {
	#if ($auth =~ /^TX:/) {
	($olat,$olon,$otime,$odepth,$omag,$orid,$auth) = dbgetv(@dbe,qw(lat lon time depth ml orid auth));
	#$erra = dbgetv(@dbe,qw(smajax));
	#$errb = dbgetv(@dbe,qw(sminax));
	#$err1 = ($erra+$errb)/2;
	#$err2 = dbgetv(@dbe,qw(sdepth));
	#$rms = dbgetv(@dbe,qw(sdobs));
	if ($omag == -999.00) {
		$omag = -2;	
	}
	$odatetime = epoch2str($otime,'%Y %m %d %H %M %S.%s');
	$ostrtime = strtime($otime);
	#print FILEOUT "# $odatetime $olat $olon $odepth $omag $err $err $rms $orid\n";
	$oyear = epoch2str($otime,"%Y");
        $omonth = epoch2str($otime,"%m");
	$ojulian = epoch2str($otime,"%j");
        $oday = epoch2str($otime,"%d");
        $ohour = epoch2str($otime,"%H");
        $omin = epoch2str($otime,"%M");
        $osec = epoch2str($otime,"%S.%s");
        #        #$osecbrief = sprintf("%02d",$osec);
        $oall1 = $omin*60;
	$oall = $oall1 + $osec;
        #
	
	@db = dbsubset(@dbo,"orid==$orid");
	@db = dbjoin(@db, dblookup(@db, "", "assoc", "" ,""));
	@db = dbjoin(@db, dblookup(@db, "", "arrival", "", ""));

 	$nassoc = dbquery(@db, "dbRECORD_COUNT");
	#$diffsec = $oall-$dbtimeprev;
	#$dbtimeprev=$oall;
       
	#$timewindow1 = $otime - 100;
	#$timewindow2 = $otime + 100;
	#@dba = dbsubset(@dbo, "origin.time >= $timewindow1 && origin.time <= $timewindow2");
	#$nevents1 = dbquery(@dba, "dbRECORD_COUNT");
	#print "number of events around here is $nevents1 $timewindow1 $timewindow2 $auth\n";
	                #2017  13 10 11  23.8500  31.41933 -103.53051   2.1150
	                #                #TX32  2017  13 10 12   0.166 P
	                #                                #TX32  2017  13 10 12  29.005 S
	                #
	if ($auth =~ /^TX:/) { 
	#if ($nevents1 < 5) { 
	#if (abs($diffsec) > 100) {   # 10 seconds differential
		
		print FILEOUT "$oyear $ojulian $ohour $omin $osec $olat $olon $odepth\n";
		print "YESSSSS\n";
		for ( $db[3] = 0; $db[3] < $nassoc; $db[3]++ ) {
			($sta, $arrtime, $deltim, $iphase) = dbgetv(@db, qw(sta arrival.time deltim iphase));
				$travtim = $arrtime-$otime;
				print "$travtim this is the travel time\n";
				$phase = substr($iphase,0,1);
				$weight = $deltim;
        			$ayear =epoch2str($arrtime,"%Y");
        			#$omonth = epoch2str($otime,"%m");
        			$ajulian = epoch2str($arrtime,"%j");
        			#$oday = epoch2str($otime,"%d");
        			$ahour = epoch2str($arrtime,"%H");
       			 	$amin = epoch2str($arrtime,"%M");
        			$asec = epoch2str($arrtime,"%S.%s");
	
		  		SWITCH: {	
		    		if ($weight <= 0.05) { $weight = 1.00;  last SWITCH;}
		    		if ($weight <= 0.1)  { $weight = 0.50;  last SWITCH;}
		    		if ($weight <= 0.2)  { $weight = 0.25;  last SWITCH;}
		    		if ($weight <= 0.4)  { $weight = 0.12;  last SWITCH;}
		    		else                 { $weight = 0.00;  last SWITCH;}
		  		} #switch

				if ($phase =~ m/P/) {
				printf FILEOUT "$sta $ayear $ajulian $ahour $amin $asec $phase\n";}
				elsif ($phase =~ m/S/) {
				printf FILEOUT "$sta $ayear $ajulian $ahour $amin $asec $phase\n";}

				#printf FILEOUT "$sta %2.3f $weight $phase\n" ,$travtim;} 
			
		}#for
		print FILEOUT "\n";
	}#if
#	}#if
#	}#if
}#for
print "Wrote hypoDD pickfile: $outfile\n"

