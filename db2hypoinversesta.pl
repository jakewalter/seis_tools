#! /usr/bin/env perl

use lib "$ENV{ANTELOPE}/data/perl/";
use Datascope;

# db2hypoinversesta.pl
#-----------------------
# Gets station data from a specific database and converts it into format for Hypoinverse
# Modified by Jake Walter (http://www.jakewalter.net/)
# from earlier versions by Andrew Newman and Brendan Sullivan, maybe others?

#################################################################################

if (  @ARGV < 2 )
 { die ( "Usage: $0 database output
  For example: $0 my_database station.hypo \n" ); 
}
use Datascope;

# Declare input variables
$db = $ARGV[0];
$output = $ARGV[1];

        #Set default min and max values for coord search and smax
	$stdate= "1900-001" ; $enddate= "2999-365" ;
        $latmin = -90 ; $latmax = 90 ;
        $lonmin = -180 ; $lonmax = 180 ;
        $Mmin = "" ;
	$Nass = 6 ;
        # If arguments exist create new lat and lon variables
	if ( $ARGV[2] ){ $stdate = $ARGV[2]; }
	if ( $ARGV[3] ){ $enddate = $ARGV[3]; }
        if ( $ARGV[4] ){ $latmin = $ARGV[4]; }
        if ( $ARGV[5] ){ $latmax = $ARGV[5]; }
        if ( $ARGV[6] ){ $lonmin = $ARGV[6]; }
        if ( $ARGV[7] ){ $lonmax = $ARGV[7]; }
        # Minimum allowable value for local magnitude
	if ( $ARGV[8] ){
                $subsetml = 1;
                $Mmin   = $ARGV[8]; 
        }else{
                $subsetml = 0;
        }
	# Minimum allowable number of associations
	if ( $ARGV[9] ){ $Nass   = $ARGV[9]; }

########################

# Open Database
print("	#-- Opening $db \n");
	@db = dbopen($db, "r+");
        # Open table origin
        @db = dblookup(@db,"","site","","");
                # Use one data with given time and spatial constraints. 
                # Also, use only analist picked data (!=UNA or orbassoc),
                # magnitude and number of associations
                 print("	#-- taking taking subset of table\n");
                  # Time


###POSSIBLE BUG for general use

		# join with origerr table
		#print("	#-- joining with table:origerr \n");
		 #@db = dbjoin(@db, dblookup(@db, "","origerr", "", "") );
                # join with event table
	
# create new TEMP file for writing
open (TMP, ">$output.tmp") || die "Can't open $output.tmp: $!" ;
print("	#-- Creating $output.tmp output \n");

# find the number of records in the database
$nrecords = dbquery(@db, "dbRECORD_COUNT" );
print("	number of stations: $nrecords \n");

# Write pertinent data to temp file
open (OUTPUT, ">$output") || die "Can't open $output: $!" ;

for( $db[3] = 0; $db[3] < $nrecords ; $db[3]++ ) {

		($stla1,$stlo1,$stel,$stnm) = dbgetv(@db, qw(lat lon elev sta));
   #($evid, $sta, $phase, $time, $deltim, $auth, $orgtime, $lat, $lon, $depth, $ml, $timeres, $timedef) = 
	#dbgetv(@db, qw(evid arrival.sta iphase arrival.time deltim origin.auth origin.time lat lon depth ml timeres timedef) );
	$sdobs = 0;
	($lat1,$ladec1) = split "\\.", $stla1;
	($lon1,$lodec1) = split "\\.", $stlo1;
	$ladec = $ladec1 /10000 * 60;
	$lodec = $lodec1 /10000 * 60;
	$n = S;
	$w = W;
	$extra = O;
	$elev = 1000 * $stel;
	printf OUTPUT (" %4s%1s%02.f%05.2f%1s%3.f%05.2f%1s\n", $stnm, $extra, abs($lat1), $ladec, $n, abs($lon1), $lodec, $w );
	print "$ladec\n";	
	
 
}

# Close TMP file
#close (TMP);
close(OUTPUT);



