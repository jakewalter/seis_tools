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

$dbname = $ARGV[0];
$outfile = "hdd_picks.dat";
open(FILEOUT, ">" , $outfile)  or die "Can't open $outfile: $!";

print "Reading database: $dbname\n";
@db = dbopen("$dbname", "r");
@dbo = dblookup(@db, "" , "origin" , "", "" );
@dbe = @dbo;
$nrecords = dbquery(@dbo, "dbRECORD_COUNT");
$err = 0.000;
$rms = 0.00;

for ( $dbe[3] = 0; $dbe[3] < $nrecords; $dbe[3]++ ) {
	($olat,$olon,$otime,$odepth,$omag,$orid) = dbgetv(@dbe,qw(lat lon time depth ml orid));
	$odatetime = epoch2str($otime,'%Y %m %d %H %M %S.%s');
	$ostrtime = strtime($otime);
	print FILEOUT "# $odatetime $olat $olon $odepth $omag $err $err $rms $orid\n";

	@db = dbsubset(@dbo,"orid==$orid");
	@db = dbjoin(@db, dblookup(@db, "", "assoc", "" ,""));
	@db = dbjoin(@db, dblookup(@db, "", "arrival", "", ""));

	$nassoc = dbquery(@db, "dbRECORD_COUNT");

	for ( $db[3] = 0; $db[3] < $nassoc; $db[3]++ ) {
		($sta, $arrtime, $deltim, $iphase) = dbgetv(@db, qw(sta arrival.time deltim iphase));

		if ($sta =~ /TAKO/ || $sta =~ /MEGW/) {
			print "Removed sta $sta from event $orid.\n";}
		else {
			$travtim = $arrtime-$otime;
			$phase = substr($iphase,0,1);
			$weight = $deltim;

	  		SWITCH: {	
	    		if ($weight <= 0.05) { $weight = 1.00;  last SWITCH;}
	    		if ($weight <= 0.1)  { $weight = 0.50;  last SWITCH;}
	    		if ($weight <= 0.2)  { $weight = 0.25;  last SWITCH;}
	    		if ($weight <= 0.4)  { $weight = 0.12;  last SWITCH;}
	    		else                 { $weight = 0.00;  last SWITCH;}
	  		} #switch

			printf FILEOUT "$sta %2.3f $weight $phase\n" ,$travtim;
		} #else
	}#for
}#for
print "Wrote hypoDD pickfile: $outfile\n"

