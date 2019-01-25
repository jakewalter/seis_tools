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
use Time::Local;

if (  @ARGV < 3 )
 { die ( "Usage: $0 database outputfile origidin" ); 
}
$outfile = hypoddpicks.pha;
$stdate= "1980-220" ; $enddate= "2099-300" ;
#if ( $ARGV[1] ){ $outfile = $ARGV[1]; }
#if ( $ARGV[2] ){ $stdate = $ARGV[2]; }
#if ( $ARGV[3] ){ $enddate = $ARGV[3]; }
$outfile = $ARGV[1];
$origidin = $ARGV[2];
$neworigid = $ARGV[3];
$yearn = $ARGV[4];
$monthn = $ARGV[5];
$dayn = $ARGV[6];
$hrn = $ARGV[7];
$minn = $ARGV[8];
$secn = $ARGV[9];
$inputcatdir = $ARGV[10];

$dbname = $ARGV[0];
#$outfile = "hdd_picks.dat";
open(FILEOUT, ">>" , $outfile)  or die "Can't open $outfile: $!";

print "Reading database: $dbname\n";
@db = dbopen("$dbname", "r");
@dbo = dblookup(@db, "" , "origin" , "", "" );
#@dbo = dbsubset(@dbo, "origin.time >= '$stdate' && origin.time <= '$enddate'");
@dbo = dbsubset(@dbo, "orid == $origidin ");
@dbe = @dbo;
$nrecords = dbquery(@dbo, "dbRECORD_COUNT");
print "There are $nrecords arrivals here !!!!!!!!!!!!\n";
$err = 0.000;
$rms = 0.00;

for ( $dbe[3] = 0; $dbe[3] < $nrecords; $dbe[3]++ ) {
	($olat,$olon,$otime,$odepth,$omag,$orid) = dbgetv(@dbe,qw(lat lon time depth ml orid));
	$odatetime = epoch2str($otime,'%Y %m %d %H %M %S.%s');
	$ostrtime = strtime($otime);
	#print FILEOUT "# $odatetime $olat $olon $odepth $omag $err $err $rms $orid\n";
	$oyear =sprintf("%02d",epoch2str($otime,"%Y"));
        $omonth = epoch2str($otime,"%m");
        $oday = epoch2str($otime,"%d");
        $ohour = epoch2str($otime,"%H");
        $omin = epoch2str($otime,"%M");
        $osec = epoch2str($otime,"%S");
        #        #$osecbrief = sprintf("%02d",$osec);
        $oall = '1' . $omonth . $oday . $ohour . $omin . $osec;
        #print "$odatetime!!!!!!!!!\n";
	
	open(FH,"<","15timesall.cat") or die "Could not open the file due to $!";
	#my $fcontent = <FH>;
	#print "$fcontent";
	$typedefs = $yearn . sprintf("%02d", $monthn) . sprintf("%02d", $dayn);
	$time1 = timegm($secn,$minn,$hrn,$dayn,$monthn,$yearn);
	$time2 = timegm(0,0,0,$dayn,$monthn,$yearn);
	$difftime1 = $time1-$time2;
	$difftime = sprintf("%d", $difftime1);
	print "$difftime this is it yooooooooo\n";
	print "$typedefs\n";
	my @lines = <FH>;
	print "Lines that matched $typedefs\n";
	for (@lines) {
    		chomp($_);
		if ($_ =~ /$difftime/) {
        	print "$_\n";
    		my @newarray = split /\s+/, $_;
		$newmag = @newarray[4];
		print "$newmag!!!!!!!!!!!!!!!!!!!!!!!!!\n";
		}
	}

#	while (my $line = <FH>) {    
   #		chomp($line);
  #  		if(grep/$line/, @typedefs){
 #     			print "$line\n";
#			print "$fcontent";
      ## perform various actions here if line match
    #	}
     # 	}
	close FH;
#	foreach ($typedefs) {
 # 		if ($fcontent =~ /$_/){
 #         		print "This is it, it really worked!!!!!!!\n";
 # 		} 
#        }
        print "# $yearn $monthn $dayn $hrn $minn $secn $olat $olon $odepth $newmag $err $err $rms $neworigid\n";
	print FILEOUT "# $yearn $monthn $dayn $hrn $minn $secn $olat $olon $odepth $newmag $err $err $rms $neworigid\n";
	@db = dbsubset(@dbo,"orid==$orid");
	@db = dbjoin(@db, dblookup(@db, "", "assoc", "" ,""));
	@db = dbjoin(@db, dblookup(@db, "", "arrival", "", ""));

 	$nassoc = dbquery(@db, "dbRECORD_COUNT");
        	
        for ( $db[3] = 0; $db[3] < $nassoc; $db[3]++ ) {
		($sta, $arrtime, $deltim, $iphase) = dbgetv(@db, qw(sta arrival.time deltim iphase));
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

			if ($phase =~ m/P/) {
			printf FILEOUT "$sta %2.3f $weight $phase\n" ,$travtim;}
			elsif ($phase =~ m/S/) {
			printf FILEOUT "$sta %2.3f $weight $phase\n" ,$travtim;} 
			
	}#for
}#for
print "Wrote hypoDD pickfile: $outfile\n"

