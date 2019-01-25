: # use perl
eval 'exec $ANTELOPE/bin/perl -S $0 "$@"'
if 0;

use lib "$ENV{ANTELOPE}/data/perl" ;
use File::Basename;
use POSIX;

# db2HYPODD
#-----------------------
# modified from the program  'db2EQKS' which was modified from 'db2hypo'.
# Gets phase data from a specific database and converts it into
# the earthqauke file that is used by TOMODD
# LAST MODIFIED BY AVN Wed Apr 17 09:45:53 EDT 2013

#################################################################################
 ($prog,$progpath,$suffix) = fileparse($0);
if (  @ARGV < 2 )
 { die ( "Usage: $prog database output [julianstartdate julianenddate] [latmin latmax lonmin lonmax][Mmin][Nass] [EIDadd]
  For example: $prog /home/data/CRSEIZE/NIC00_240/db/NIC00_240 test.EQKS  2000-240 2000-250 9.5 10.5 -86.25 -84.25 0.0 10 2200000 
       or 
               $prog NICOYA NICOYA.EQKS \n" ); 
}
use Datascope;

# Declare input variables
$db = $ARGV[0];
$output = $ARGV[1];
$origidin = $ARGV[2];
$neworigid = $ARGV[3];
$yearn = $ARGV[4];
$monthn1 = $ARGV[5];
$monthn = sprintf("%02d",$monthn1);
$dayn1 = $ARGV[6];
$dayn = sprintf("%02d",$dayn1);
$hrn1 = $ARGV[7];
$hrn = sprintf("%02d",$hrn1);
$minn1 = $ARGV[8];
$minn = sprintf("%02s",$minn1);
$secna = $ARGV[9];
#$secn1 = sprintf("%02f",$secna);
$secn = sprintf("%02.f",$secna);
$secn = $secna;
$daysecondsn1 = $ARGV[10];
$dayseconds = sprintf("%08.f",$dayseconds);

#########

# Open Database
print("	#-- Opening $db and dayseconds = $daysecondsn \n");
	@db = dbopen($db, "r");
        # Open table origi
        @db = dblookup(@db,"","origin","","");
	@db = dbsubset(@db, "orid == '$origidin' ");
	@db = dbjoin(@db, dblookup(@db, "", "assoc", "" ,""));
	@db = dbjoin(@db, dblookup(@db, "", "arrival", "" ,""));
	@db = dbjoin(@db, dblookup(@db, "","origerr", "", "") );
	@db = dbjoin(@db, dblookup(@db, "","event", "", "") );         
# create new TEMP file for writing
open (TMP, ">$output.tmp") || die "Can't open $output.tmp: $!" ;
print("	#-- Creating $output.tmp output \n");

# find the number of records in the database
$nrecords = dbquery(@db, "dbRECORD_COUNT" );
print("	#-- number of arrivals: $nrecords \n");

# Write pertinent data to temp file
for( $db[3] = 0; $db[3] < $nrecords ; $db[3]++ ) {
   ($evid, $sta, $phase, $time, $deltim, $auth, $orgtime, $lat, $lon, $depth, $ml, $sdobs, $timeres, $timedef) = 
	dbgetv(@db, qw(evid arrival.sta iphase arrival.time deltim origin.auth origin.time lat lon depth ml sdobs timeres timedef) );
   print TMP ($evid+$EIDadd," ", $sta," ", $phase," ", $time," ", $deltim," ", $auth," ", $orgtime," ", $lat," ", $lon," ", $depth," ", $ml," ", $sdobs," ", $timeres," ", $timedef,"\n");
}

# Close TMP file
close (TMP);

###############################

# Reopen TMP file for reading only
open(FILE, "$output.tmp");
# create new OUTPUT files for writing
open (OUTPUT, ">>$output") || die "Can't open $output: $!" ;
open (OUTPUTad, ">>$output.absolute.data") || die "Can't open $output.absolute.data: $!" ;
open (OUTPUTec, ">>$output.event.cat") || die "Can't open $output.event.cat: $!" ;

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
	#collect and pring header information only if its a new event
	 if ($newevents eq 1 ){
		#$date = epoch2str($orgtime, "%Y %m %d %H %M %S.%s" ) ;
		#$dateec = epoch2str($orgtime, "%Y%m%d %H%M%S%s" ) ;
		#$dateec = epoch2str($orgtime, "%Y%m%d %H%M%S%s" ) ;
		print "$orgtime\n";
		
		$dateec = substr($dateec,0,17) ;
         	($secna1, $secnb) = (split /\./,$secn);
		$secna = sprintf("%02d",$secna1);
		#$secnb = substr($secn,-2,2);
		print "Check this dammit .......................################# $secn $secna $secnb ######## $hrn $minn\n";
		($lat,$lon,$dep,$mag) = (split / +/, $line[$i])[7,8,9,10];
		   $lat1 = $lat; $lon1 = $lon;
		   for ($i1=0; $i1 < 5; $i1++) {
		      chop($lat1); chop($lon1);
  		   }
		   $lat2 = ($lat - $lat1) * 60; $lon2 = abs(($lon - $lon1) * 60);
		if ( $mag lt 0 ) {$mag = 0.00};
                $mag2=0; $mag3=0; $mag4=0; $id="000000"; 
	 	printf OUTPUT ("# $yearn $monthn $dayn $hrn $minn $secn %9.4f %10.4f %6.2f %4.2f %4.2f %4.2f %4.2f %10s \n", $lat, $lon, $dep, $mag, $mag2, $mag3, $mag4, $neworigid ); 
	 	printf OUTPUTad ("# $neworigid\n" ); 
	 	printf OUTPUTec ("$yearn$monthn$dayn $hrn$minn$secna$secnb %7.4f %7.4f %6.2f %6.2f %5s %5s %5s %8s     0\n", $lat, $lon, $dep, $mag, $mag2, $mag3, $mag4, $neworigid );
		#printf OUTPUTec ("$dateec %7.4f %7.4f %6.2f %6.2f %5s %5s %5s %8s     0\n", $lat, $lon, $dep, $mag, $mag2, $mag3, $mag4, $neworigid ); 
	 	# no longer a newevent
	 	$newevents=0;
	 }
        ($phase,$arvtime) = (split / +/, $line[$i])[2,3];
	$phase = substr($phase,0,1);
        $sta_qual=1;
       # print phase information only if it is listed as a P or S
	if ($phase eq "P" || $phase eq "S"){

		$Dsec = $arvtime-$orgtime;
        	printf OUTPUT ("%4s  %6.3f %5.3f  %1s\n", $sta1, $Dsec, $sta_qual, $phase );
        	printf OUTPUTad ("%4s  %6.3f %5.3f  %1s\n", $sta1, $Dsec, $sta_qual, $phase );
		$narrivals++;
       
	} else { printf ( "	#----- Skipping phase=$phase \n");} 
	# if the next line is a new event
        if ($evid1 != $evid2) { 
          $nevts++;
	  $newevents=1;
	  $narrivals=0;
        }
       
}   # end of ILOOP loop
printf("	#-- number of events: %d\n", $nevts);

close(FILE);
close(OUTPUT);
close(OUTPUTad);
close(OUTPUTec);
unlink("$output.tmp");
