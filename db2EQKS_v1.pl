#! /usr/bin/env perl

use lib "$ENV{ANTELOPE}/data/perl/";
use Datascope;

# db2EQKS
#-----------------------
# modified from the program 'db2hypo'.
# Gets phase data from a specific database and converts it into
# the EQKS file that is used by simulps14 wich is the same as the travel time 
# output from hypoinverse.
# LAST MODIFIED BY AVN Thu Jul  6 15:04:37 EDT 2006

#################################################################################

if (  @ARGV < 2 )
 { die ( "Usage: $0 database output [julianstartdate julianenddate] [latmin latmax lonmin lonmax][Mmin][Nass]
  For example: $0 /auto/proj/osa/DATASCOPE/CONTOBS/db/osa_cont osa.EQKS 1999-267 1999-334 7.5 10.15 -85.25 -82.25 0.0 10 
       or 
               $0 NICOYA NICOYA.EQKS \n" ); 
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
	$Nass = 5 ;
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
        @db = dblookup(@db,"","origin","","");
                # Use one data with given time and spatial constraints. 
                # Also, use only analist picked data (!=UNA or orbassoc),
                # magnitude and number of associations
                 print("	#-- taking taking subset of table\n");
                  # Time
                   @db = dbsubset(@db, "origin.time >= '$stdate' && origin.time <= '$enddate'");
                  # Space
                   @db = dbsubset(@db, "origin.lat >= '$latmin' && origin.lat <= '$latmax'");
                   @db = dbsubset(@db, "origin.lon >= '$lonmin' && origin.lon <= '$lonmax'");

###POSSIBLE BUG for general use
                  # author
                   @db = dbsubset(@db, "origin.auth != 'orbassoc' && origin.auth != 'antassoc' && origin.auth != 'UNA'" );
########
                  # magnitude 
                   if ($subsetml == "1") { @db = dbsubset(@db, "origin.ml >= '$Mmin'" ); }
		  # number of associations
		   @db = dbsubset(@db, "origin.nass >= '$Nass' ");
		
		# join with origerr table
		#print("	#-- joining with table:origerr \n");
		 #@db = dbjoin(@db, dblookup(@db, "","origerr", "", "") );
                # join with event table
                 print("	#-- joining with table:event \n");
                 @db = dbjoin(@db, dblookup(@db, "","event", "", "") );
                # Use only data that is the prefered event
                 print("	#-- taking taking subset of table\n");
                 @db = dbsubset(@db, " event.prefor == origin.orid" );
                # join with assoc table
                 print("	#-- joining with table:assoc \n");
                 @db = dbjoin(@db, dblookup(@db, "","assoc", "", "") );
                # join with arrival table
                 print("	#-- joining with table:arrival \n");
                 @db = dbjoin(@db, dblookup(@db, "","arrival", "","") );
                # Sort data on time, then station then phase
                 print("	#-- sorting data from database \n");
                 @db = dbsort(@db, "origin.time", "sta","iphase");

# create new TEMP file for writing
open (TMP, ">$output.tmp") || die "Can't open $output.tmp: $!" ;
print("	#-- Creating $output.tmp output \n");

# find the number of records in the database
$nrecords = dbquery(@db, "dbRECORD_COUNT" );
print("	#-- number of arrivals: $nrecords \n");

# Write pertinent data to temp file

for( $db[3] = 0; $db[3] < $nrecords ; $db[3]++ ) {
   ($evid, $sta, $phase, $time, $deltim, $auth, $orgtime, $lat, $lon, $depth, $ml, $timeres, $timedef) = 
	dbgetv(@db, qw(evid arrival.sta iphase arrival.time deltim origin.auth origin.time lat lon depth ml timeres timedef) );
	$sdobs = 0;
   print TMP ($evid," ", $sta," ", $phase," ", $time," ", $deltim," ", $auth," ", $orgtime," ", $lat," ", $lon," ", $depth," ", $ml," ", $sdobs," ", $timeres," ", $timedef,"\n");
}

# Close TMP file
close (TMP);
print "$timeres $timedef";
###############################

# Reopen TMP file for reading only
open(FILE, "$output.tmp");
# create new OUTPUT file for writing
open (OUTPUT, ">$output") || die "Can't open $output: $!" ;

# set ILOOP to test all records in TMP file
@line = <FILE>;
$nevts = 0;
$newevents=1;
$narrivals=0;
ILOOP: for ($i = 0; $i < $nrecords; $i++) {
        $j = $i + 1;
        chomp $line[$i];
        ($evid1,$sta1,$orgtime) = (split / +/, $line[$i])[0,1,6];
	if ($j != $nrecords){
		chomp $line[$j];
        	($evid2) = (split / +/, $line[$j])[0];
	 } else { $evid2 = 00 ; }
	# only do when there is a new event
	 if ($newevents eq 1 ){
		$date1 = epoch2str($orgtime, "%y%m%d %H%M %S.%s" ) ;
		$date = epoch2str($orgtime, "%y%m%d %H%M %S" ) ;
		print "$date\n";
		$msec = substr($date1,15,2) ;
		print "$msec\n";
         	($lat,$lon,$dep,$mag) = (split / +/, $line[$i])[7,8,9,10];
		   $lat1 = $lat; $lon1 = $lon;
		   for ($i1=0; $i1 < 5; $i1++) {
		      chop($lat1); chop($lon1);
  		   }
		   $lat2 = ($lat - $lat1) * 60; $lon2 = abs(($lon - $lon1) * 60);
		if ( $mag lt 0 ) {$mag = 0.00};
	 	printf OUTPUT ("$date.$msec%3s %5.2f%4s %5.2f%7.2f  %5.2f\n", $lat1, $lat2, abs($lon1), $lon2, $dep, $mag ); 
	 	# no longer a newevent
	 	$newevents=0;
	 }
        ($phase,$arvtime) = (split / +/, $line[$i])[2,3];
	$phase = substr($phase,0,1);
	if ($phase eq "P" || $phase eq "S"){

		$Dsec = $arvtime-$orgtime;
        	printf OUTPUT ("%4s %1s 0%6.2f", $sta1, $phase, $Dsec);
		$narrivals++;
        	if ( (($narrivals) % 6) == 0 && $evid1 == $evid2) { printf OUTPUT ("\n"); }
       
	} else { printf ( "	#----- Skipping phase=$phase \n");} 
	# if the next line is a new event, print the terminator line  
        if ($evid1 != $evid2) { 
            printf OUTPUT ("\n0\n");
          $nevts++;
	  $newevents=1;
	  $narrivals=0;
        }
       
}   # end of ILOOP loop
printf("	#-- number of events: %d\n", $nevts);

close(FILE);
close(OUTPUT);

