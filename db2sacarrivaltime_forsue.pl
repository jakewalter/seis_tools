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

if (  @ARGV < 3 )
 { die ( "Usage: $0 database day_volumes outputdir [start] [enddate] " ); 
}

$dbname = $ARGV[0];
#$outdir = "/home/jwalter9/nicoyaquake";
$db = $ARGV[0];

$dayvol = $ARGV[1];
$stdate= "1980-220" ; $enddate= "2099-300" ;
if ( $ARGV[2] ){ $outdir = $ARGV[2]; }
if ( $ARGV[3] ){ $stdate = $ARGV[3]; }
if ( $ARGV[4] ){ $enddate = $ARGV[4]; }
	
#open(FILEOUT, ">" , $outdir)  or die "Can't open $outdir: $!";

print "Reading database: $dbname\n";
@db = dbopen("$dbname", "r");
@dbo = dblookup(@db, "" , "origin" , "", "" );
@dbo = dbsubset(@dbo, "origin.time >= '$stdate' && origin.time <= '$enddate'");
#@dbo = dbsubset(@dbo,"orid>=12573");    #   12573
@dbo = dbsubset(@dbo, "origin.nass >= 8 ");
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
	system("mkdir $outdir/$oall");

	printf FILEOUT3 "$oall $oyear $omonth $oday $ohour $omin $osec $olat $olon $odepth $omag\n";
	$datej=`date -d "$oyear/$omonth/$oday" +%j`;
	
	@dayvoldir= <$dayvol/*/*H*$datej>;
	foreach $tablea (@dayvoldir) {

      #chomp (@tablea[$i]);
	($field0, $field1,$field2,$field3,$field5,$sta,$file1) = split '/', $tablea;
	print "$tablea";
	($field1,$field2,$field3,$chan,$year,$day) = split "\\.", $file1;
	#$names = $sta . $chan . $year . $day . '.sac';

	#chdir $sta;

	
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
			print "$sta $chan $cstart $cend";

		`db2sac -sc $sta:$chan -ts $cstart -te $cend -gap interp -i $dbname .`;
			
			


print "$outdir/$oall/YZ.$sta.$chan.SAC.bp";
`sac << END
r sac/*$chan
rmean
synch
ch evla $olat
ch evlo $olon
ch evdp $odepth
ch o 0
w $outdir/$oall/YZ.$sta.$chan.SAC.bp
quit
END`;
#printf FILEOUT1 "$sta\n";
#printf FILEOUT2 "YZ.$sta.$chan.SAC.bp 10 10 1\n";

			`rm sac/*$chan`;
#			$travtim = $arrtime-$otime;
#			$phase = substr($iphase,0,1);
#			$weight = $deltim;
$i = $i + 1;
}

			#printf FILEOUT "$sta %2.3f $weight $phase\n" ,$travtim;
		#} #else

#`saclst o f *.SAC* | gawk '{printf "r %s\nch allt %.5f\nwh\n",$1,$2*(-1)} END{print "quit"}' | sac`;
}#for
print "All files in $outdir\n"

