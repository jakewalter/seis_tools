#! /usr/bin/env perl
#-----------------------
# db2sacarrivaltime.pl
# Antelope database perl script to cut catalog data for event waveforms
# Creates files necessary for cross-correlation
# 
# you must have perl package "Datascope.pm"
# the "use lib" line points to where antelope keeps it (user may need to change
# Requires programs: sac, db2sac (should be there if Antelope is setup properly)
#
# USAGE: db2sacarrivaltime_v1.pl waveformdb destination_dir [start-time] [end-time]
# [start-time] [end-time] are optional
# Example db2sacarrivaltime_v1.pl /home/jwalter9/nicoyaclean/nicclean /home/jwalter9/nicoyaquake/TempWaveform 2012-240 2012-241
# Database must contain 'origin', 'assoc', and 'arrival' tables
#  

use lib "$ENV{ANTELOPE}/data/perl/";
use Datascope;

if (  @ARGV < 3 )
 { die ( "Usage: $0 database contdir outputdir [netcode] [start] [enddate]" ); 
}

$dbname = $ARGV[0];
#$outdir = "/home/jwalter9/nicoyaquake";
$db = $ARGV[0];
$contdir = $ARGV[1];

$net = XX;
$stdate= "1980-220" ; $enddate= "2099-300" ;
if ( $ARGV[2] ){ $outdir = $ARGV[2]; }
if ( $ARGV[3] ){ $net = $ARGV[3]; }
if ( $ARGV[4] ){ $minassoc = $ARGV[4]; }
if ( $ARGV[5] ){ $stdate = $ARGV[5]; }
if ( $ARGV[6] ){ $enddate = $ARGV[6]; }

print "Network name: $net\n";
#open(FILEOUT, ">" , $outdir)  or die "Can't open $outdir: $!";

print "Reading database: $dbname\n";
@db = dbopen("$dbname", "r");
@dbo = dblookup(@db, "" , "origin" , "", "" );
@dbo = dbsubset(@dbo, "origin.time >= '$stdate' && origin.time <= '$enddate'");
#@dbo = dbsubset(@dbo,"orid==8536");    #   12573
@dbo = dbsubset(@dbo, "origin.nass >= $minassoc");
#@dbo = dbsubset(@dbo, "origin.lat > 31.5");
@dbe = @dbo;
$nrecords = dbquery(@dbo, "dbRECORD_COUNT");
$err = 0.00;
$rms = 0.00;

print "Output will go here: $outdir\n";
open(FILEOUT3, ">>" , "$outdir/catalog")  or die "Can't open catalog file: $!";
#open(FILEOUT5, ">" , "$outdir/origid.dat")  or die "Can't open catalog file: $!";
#print "$nrecords";

for ( $dbe[3] = 0; $dbe[3] < $nrecords; $dbe[3]++ ) {
	$progress = $dbe[3]+1;
	print "Event number: $progress of $nrecords\n";
	
	($olat,$olon,$otime,$odepth,$omag,$orid,$auth) = dbgetv(@dbe,qw(lat lon time depth ml orid auth));
	print "Origin id: $orid $otime\n";
	$odatetime = epoch2str($otime,'%Y %m %d %H %M %S.%s');
	$ostrtime = strtime($otime);
	
	$oyear = epoch2str($otime,"%Y");
	$omonth = epoch2str($otime,"%m");
	$oday = epoch2str($otime,"%d");
	$ohour = epoch2str($otime,"%H");
	$omin = epoch2str($otime,"%M");
	$osec = epoch2str($otime,"%S");
	$osecbrief = sprintf("%02d",$osec);
	$oall = $oyear . $omonth . $oday . $ohour . $omin . $osecbrief;
	$ofractionday1 = $ohour/24.0;
        $ofractionday2= $omin/1440.0;
        $ofractionday3 = $osec/86400.0;
        
        $ofractionday = $ofractionday1+$ofractionday2+$ofractionday3;
        $osecondsday = $ofractionday*86400.0;

	#print FILEOUT "# $odatetime $olat $olon $odepth $omag $err $err $rms $orid\n";
	if ($auth =~ /^TX:/) {
	@db = dbsubset(@dbo,"orid==$orid");
	@db = dbjoin(@db, dblookup(@db, "", "assoc", "" ,""));
	@db = dbjoin(@db, dblookup(@db, "", "arrival", "", ""));

	$nassoc = dbquery(@db, "dbRECORD_COUNT");
	system("mkdir $outdir/$oall");
	#mkdir $oall unless -d $oall;
	#print "$oall\n";
	printf FILEOUT3 "$oall $oyear $omonth $oday $ohour $omin $osec $olat $olon $odepth $omag\n";
	print "$oall $oyear $omonth $oday $ohour $omin $osec $olat $olon $odepth $omag $nassoc\n";
	#open(FILEOUT1, ">" , "$oall/stn.id")  or die "Can't open stn.id: $!";
	#open(FILEOUT2, ">" , "$oall/wf_SNR.dat")  or die "Can't open wf_SNR.dat: $!";
	#open(FILEOUT4, ">" , "$oall/phases.dat")  or die "Can't open phases.dat: $!";
	open(FILEOUT1, ">" , "$outdir/$oall/stn.id")  or die "Can't open stn.id: $!";
	open(FILEOUT2, ">" , "$outdir/$oall/wf_SNR.dat")  or die "Can't open wf_SNR.dat: $!";
	open(FILEOUT4, ">" , "$outdir/$oall/phases.dat")  or die "Can't open phases.dat: $!";
	open(FILEOUT5, ">" , "$outdir/$oall/origid.dat")  or die "Can't open catalog file: $!";
	printf FILEOUT5 "$orid\n";
	close(FILEOUT5);
          #open(FILEOUT3, ">" , "$outdir/catalog")  or die "Can't open catalog file: $!";
print "$oall\n";
##### Now for each arrival ...
	for ( $db[3] = 0; $db[3] < $nassoc; $db[3]++ ) {
		($sta, $chan1, $arrtime, $deltim, $iphase) = dbgetv(@db, qw(sta chan arrival.time deltim iphase));
		$chan = sprintf("%.3s",$chan1);
		if ($sta =~ m/WMOK/) {
			if ($chan =~ m/BHN/) {
        		$chan = 'BH1';}
        		if ($chan =~ m/BHE/) {
        		$chan = 'BH2';}
		}
		if ($sta =~ m/NATX/) {
			if ($chan =~ m/BHN/) {
        		$chan = 'BH1';}
        		if ($chan =~ m/BHE/) {
        		$chan = 'BH2';}
		}
		printf FILEOUT1 "$sta $phase\n";
		printf FILEOUT2 "$net.$sta.$chan.SAC.bp 10 10 1\n";
		printf FILEOUT4 "$sta $chan $phase\n";

			##### cut 5 sec and 10 after arrival time at station
			$cut0 = $arrtime;
			#$cut1 = $otime + 120;
			$tempday0 = `date -d "$oyear-$omonth-$oday 00:00:00" +%s`;
			
			$cyear = epoch2str($cut0,"%Y");
			$cmonth = epoch2str($cut0,"%m");
			$cday = epoch2str($cut0,"%d");
			$chour = epoch2str($cut0,"%H");
			$cmin = epoch2str($cut0,"%M");
			$csec = epoch2str($cut0,"%S.%s");
			
			$fractionday1 = $chour/24.0;
			$fractionday2= $cmin/1440.0;
			$fractionday3 = $csec/86400.0;
			$fractionday = $fractionday1+$fractionday2+$fractionday3;
			$secondsday = $fractionday*86400.0;
			#print "$chour $cmin $csec $secondsday $fractionday\n";

			#$cut0 = $secondsday - 5;
			$cut0 = $secondsday - 5;
			$cut1 = $secondsday + 10;

		#	$cmin1 = epoch2str($cut1,"%M");
		#	$csec1 = epoch2str($cut1,"%S.%s");

		#	$datej=`date -d "$cyear/$cmonth/$cday" +%j`;
		#	$cstart = $cyear . ':' . sprintf("%03d",$datej) . ':' . $chour . ':' . $cmin0 . ':' . $csec0;
		#	$cend = $cyear . ':' . sprintf("%03d",$datej) . ':' . $chour . ':' . $cmin1 . ':' . $csec1;
			
			#$date1=`date -d "$year1-01-01 +$j days -1 day" "+%Y/%m/%d"`;    ### convert from DOY to Y/m/d

			##########db2sac -sc T14A:BH* -ts 2007:146:23:45:23 -te 2007:146:23:50:23 /home/jwalter9/nicoyaclean/nicclean $outdir/ContWaveform
			#`db2sac -sc $sta:$chan -ts $cstart -te $cend -gap interp -i $dbname .`;
			$phase = substr($iphase,0,1);
			$again = 0;
			if ($phase =~ m/P/) {
			$flag = "t1";
			}
			elsif ($phase =~ m/S/) {
			$flag = "t2";
			$again = 1;
			}


$shift = $secondsday;
#$shift = $arrtime - $otime;
#$flag = "t2";
#print "$cut0 $cut1 $shift\n";
$onegsecondsday = $osecondsday*(-1);
print "$osecondsday $cut0 $cut1 $shift\n";
print "$contdir/$oyear$omonth$oday/$net.$sta.$chan.SAC.bp\n";
print "$outdir/$oall/$net.$sta.$chan.SAC.bp\n";
`sac << END
cut o $cut0 $cut1
r $contdir/$oyear$omonth$oday/$net.$sta.$chan.SAC.bp
transfer to wa
ch evla $olat
ch evlo $olon
ch evdp $odepth
ch o $osecondsday
ch norid $orid
ch $flag $shift
wh
ch allt $onegsecondsday
wh
w $outdir/$oall/$net.$sta.$chan.SAC.bp
quit
END`;

if ($again = 1) {	
	    		if ($chan =~ m/BHE/) {
			$chan = "BHN";}
			elsif ($chan =~ m/SHE/) {
			$chan = "SHN";}
			elsif ($chan =~ m/EHE/) {
			$chan = "EHN";}
			elsif ($chan =~ m/HHE/) {
			$chan = "HHN";}
			elsif ($chan =~ m/HH1/) {
			$chan = "HH2";}
			elsif ($chan =~ m/BH1/) {
			$chan = "BH2";}

			elsif ($chan =~ m/BHN/) { 
			$chan = "BHE";}
			elsif ($chan =~ m/SHN/) { 
			$chan = "SHE";}
			elsif ($chan =~ m/EHN/) { 
			$chan = "EHE";}
			elsif ($chan =~ m/HHN/) { 
			$chan = "HHE";}
			elsif ($chan =~ m/HH2/) {
			$chan = "HH1";}
			elsif ($chan =~ m/BH2/) {
			$chan = "BH1";}

			#$flag = "t2";
			#print "$cut0 $cut1 $shift\n";
		#printf FILEOUT1 "$sta $phase\n";
		printf FILEOUT2 "$net.$sta.$chan.SAC.bp 10 10 1\n";
		#printf FILEOUT4 "$sta $chan $phase\n";
`sac << END
cut o $cut0 $cut1
r $contdir/$oyear$omonth$oday/$net.$sta.$chan.SAC.bp
ch evla $olat
ch evlo $olon
ch evdp $odepth
ch o $osecondsday
ch norid $orid
ch $flag $shift
wh
ch allt $onegsecondsday
wh
w $outdir/$oall/$net.$sta.$chan.SAC.bp
quit
END`;
		}




	}#for
	close(FILEOUT1);
	close(FILEOUT2);
	close(FILEOUT4);


#			$travtim = $arrtime-$otime;
#			$phase = substr($iphase,0,1);
#			$weight = $deltim;


			#printf FILEOUT "$sta %2.3f $weight $phase\n" ,$travtim;
		#} #else
#`gsact $oyear $omonth $oday $ohour $omin $osec 00 f $outdir/$oall/*bp | gawk '{printf "r \$1\nch o \$2\nwh\n"} END{print "quit"}' | sac`;
#saclst o f $outdir/$oall/*.SAC* | gawk '{printf "r %s\nch allt %.5f\nwh\n",$1,$2*(-1)} END{print "quit"}' | sac
#`saclst o f *.SAC* | gawk '{printf "r %s\nch allt %.5f\nwh\n",\$1,\$2*(-1)} END{print "quit"}' | sac`;
}#if
}#for
close(FILEOUT3);
print "All files in $outdir\n"

