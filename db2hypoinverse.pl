#! /usr/bin/env perl
#-----------------------
# db2hypoinverse.pl
# Antelope database perl script
#
# Produces a phase pickfile for hypoinverse
# from an Antelope CSS 3.0 database
#
# you must have perl package "Datascope.pm"
# the "use lib" line points to where antelope keeps it
#
# USAGE: db2hypoinverse.pl my_database phasefilename
# Database must contain 'origin', 'assoc', and 'arrival' tables
# OUTPUT: file "hdd_picks.dat"
# Script by Jake Walter http://www.jakewalter.net/
# Modified from scripts by Andrew Newman, Heather DeShon, and others

use lib "$ENV{ANTELOPE}/data/perl/";
use Datascope;

if (  @ARGV < 1 )
 { die ( "Usage: $0 database [outputfile] [start] [enddate]" ); 
}
$outfile = hypoinvpickspha;
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
	($olat,$olon,$otime,$odepth,$omag,$orid,$auth) = dbgetv(@dbe,qw(lat lon time depth ml orid auth));
	$odatetime = epoch2str($otime,'%Y %m %d %H %M %S.%s');
	$ostrtime = strtime($otime);
	

	@db = dbsubset(@dbo,"orid==$orid");
	@db = dbjoin(@db, dblookup(@db, "", "assoc", "" ,""));
	@db = dbjoin(@db, dblookup(@db, "", "arrival", "", ""));

	$nassoc = dbquery(@db, "dbRECORD_COUNT");

	#if ($auth =~ /^TX:/) { 
		print FILEOUT "\n";
		for ( $db[3] = 0; $db[3] < $nassoc; $db[3]++ ) {
			($sta, $arrtime, $deltim, $iphase) = dbgetv(@db, qw(sta arrival.time deltim iphase));
			
				$expt = PAN;
				$cut0 = $arrtime;
				$cyear1 = epoch2str($cut0,"%Y");
				$cyear = substr($cyear1, -2);
				$cmonth = epoch2str($cut0,"%m");
				$cday = epoch2str($cut0,"%d");
				$chour = epoch2str($cut0,"%H");
				$cmin1 = epoch2str($cut0,"%M");
				$cmin = sprintf("%02d",$cmin1);
				$csec2a = epoch2str($cut0,"%S.%s");
				$csec2 = sprintf("%05.2f",$csec2a);
				$arrivaltime = $cyear . $cmonth . $cday . $chour . $cmin . $csec2;
				#$stastring = $sta . $expt;
				print "$iphase\n";
				#SR04IPU0 691005111258.05       62.45ISU0   29. .20        0.78
				#SRO4 is the station name
				#IPU0 means P-arrival phase (U means the first motion is up, D means down)
				#6910051112 is the date and time of the event in yr-mt-dy-hr-mi format
				#58.05 is the seconds for P-arrival
				#62.45 is the seconds for S-arrival
				#ISU0 means the S-arrival phase
				#29. is the maximum peak-to-peak amplitude in mm
				#.20 is the period of maximum amplitude in second
				#0.78 is the weight assigned to this station.
				if ($iphase =~ m/P/) {
				#$printf OUTPUT ("%4s%2.f%1s%05.2f %3.f%1s%05.2f %4.f %4.f %4.f %2.f %2.f\n", $sta, $expt, $n, $ladec, abs($lon1), $w, $lodec, $elev,0,0,0,0 );
				printf FILEOUT ("$sta P   $arrivaltime\n");
				}
				elsif ($phase =~ m/S/) {
				#printf FILEOUT ("$sta                           $csec2 S\n");
				print "Found it!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n";
				}
				 
		}
	#}			
}
print "Wrote hypoinverse pickfile: $outfile\n"

