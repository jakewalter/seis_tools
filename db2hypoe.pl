: # use perl
eval 'exec perl -S $0 "$@"'
if 0;

# db2hypoe
# ----------------
# This program converts arrival tables to the hypoellipse station format
# Written by Heather DeShon, 4/16/2012.
#Revised to deal with ZW4F	

use lib "$ENV{ANTELOPE}/data/perl";

if (  @ARGV != 4 )
    { die ( "Usage: $0 database [output].pha julianstartdate julianenddate  \n" ); }

use Datascope;

$db = $ARGV[0];
$output = $ARGV[1];
$stdate = $ARGV[2];
$enddate = $ARGV[3];
#$auth = $ARGV[4];  #accepted: hwithers or all

@db = dbopen($db, "r+");
@db = dblookup(@db,"","arrival","","");
@db = dbjoin(@db, dblookup(@db, "", "assoc", "", "") );
@db = dbjoin(@db, dblookup(@db, "", "origin", "","") );
@db = dbjoin(@db, dblookup(@db, "", "event", "","") );
@db = dbsubset(@db, "origin.orid == event.prefor");
@db = dbsubset(@db, "origin.auth!='NEIC:PDEMl' || origin.auth!='oalMl'"); 

@db = dbsubset(@db, "lat>=32 && lat<34 && lon>=-100 && lon<-95");
@db = dbsubset(@db, "ndef>=8"); 
@db = dbsort(@db, "origin.time", "sta", "iphase");
@db = dbsubset(@db, "origin.time >= '$stdate' && origin.time <= '$enddate'" );

open (TMP, ">$db.hypoe") || die "Can't open tmp.file: $!" ;
open (OUTPUT, ">$output") || die "Can't open $output: $!" ;

$nrecords = dbquery(@db, "dbRECORD_COUNT" );
print "$nrecords\n";

for( $db[3] = 0; $db[3] < $nrecords ; $db[3]++ ) {
   ($evid, $sta, $phase, $time, $deltim, $delta, $auth, $orgtime, $lat, $lon, $depth, $mag, $timeres, $timedef,$arvauth,$chan) = 
   	dbgetv (@db, qw(evid sta iphase time deltim delta origin.auth origin.time lat lon depth ml timeres timedef arrival.auth chan ) );
   #if ($sta =~ /^S/) { $sta = "S" . $sta ; }

   printf TMP (" %d     %4s     %1s     %15.5f     %8.3f  %6.3f   %15s     %15.5f %6.4f %8.4f %8.4f %4.2f %8.4f %4s %s %s\n", 
               $evid, $sta, $phase, $time, $delta, $deltim, $auth, $orgtime, $lat, $lon, $depth, $mag, $timeres, $timedef, $arvauth,$chan);
}
close (TMP);

open(FILE, "$db.hypoe");

@line = <FILE>;
$k = 0;
ILOOP: for ($i = 0; $i < @line-1; $i++) {
         $j = $i + 1;
         chomp $line[$i];
         chomp $line[$j];

	 $evid1 = (split /\s+/,$line[$i])[1]*1;
         $evid2 = (split /\s+/,$line[$j])[1]*1;
	 if ($evid1 != $evid2) { $k=0; }
 
	 ($sta1,$orgtime,$lat,$lon,$depth,$mag)=(split /\s+/,$line[$i])[2,8,9,10,11,12];
         ($sta2,$orgtime2,$lat2,$lon2,$depth2,$mag2)=(split /\s+/,$line[$j])[2,8,9,10,11,12];
 
	 $orgyear = epoch2str($orgtime, "%Y");
	 $orgmon = epoch2str($orgtime, "%m");
	 $orgday = epoch2str($orgtime, "%d");
	 $orghr = epoch2str($orgtime, "%H");
	 $orgmin = epoch2str($orgtime, "%M");
	 $orgsec = epoch2str($orgtime, "%S");
         $orgsec2 = epoch2str($orgtime, "%s");
	 $orgsec2 = substr($orgsec2,0,2);
 	
         if ($lat<0) { $NS="S"; $lat=$lat*-1; } else { $NS="N"; } 
         if ($lon<0) { $EW="W"; $lon=$lon*-1; } else { $EW="E"; }
	 ($latd,$lats) = (split /\./,$lat)[0,1];
         ($lond,$lons) = (split /\./,$lon)[0,1];
         $lats = ".".$lats; $lats = $lats * 60.0; $lats=sprintf("%4.2f",$lats); $lats=$lats*100; 
         $lons = ".".$lons; $lons = $lons * 60.0; $lons=sprintf("%4.2f",$lons); $lons=$lons*100;
         $depth = sprintf("%3.2f",$depth); $depth=$depth*100;
         if ($mag == -999.00) { $mag = 0.00;}
	 $mag = sprintf("%2.1f",$mag); $mag=$mag*10; 
	 $y2k="/";
	
	if ($evid1 == $evid2 && $k == 0) {
		if ($i!=0) { print OUTPUT "C*(C) SMU catalog accessed Nov. 2016\n                 1010.00\n"; }
         	printf OUTPUT ("%4d%2d%2d%2d%2d%2d%2d%2d%1s%4d%3d%1s%4d%5d%2d%45s\n",
		 	$orgyear, $orgmon, $orgday, $orghr, $orgmin, $orgsec, $orgsec2, $latd,$NS, $lats, $lond, $EW, $lons,$depth,$mag,$y2k); 
		$k++;
		$usarray=0; $holly=0; $hh=0; 
         } elsif ( $evid1 ne $oldevid ) { 
		print OUTPUT "C*(C) SMU catalog accessed Nov. 2016\n                 1010.00\n";
		printf OUTPUT ("%4d%2d%2d%2d%2d%2d%2s%2d%1s%4d%3d%1s%4d%5d%2d%45s\n",
                        $orgyear, $orgmon, $orgday, $orghr, $orgmin, $orgsec, $orgsec2, $latd,$NS, $lats, $lond, $EW, $lons,$depth,$mag,$y2k);
		$k=1;
		$usarray=0; $holly=0; $hh=0;
	}

	 ($phase,$arvtime,$deltime,$arvauth,$chan)=(split /\s+/,$line[$i])[3,4,6,15,16];
         ($phase2,$arvtime2,$deltime2,$arvauth2)=(split /\s+/,$line[$j])[3,4,6,15];

	 if ($arvauth =~ /:/) { $arvauth=(split /:/,$arvauth)[1]; }
         if ($phase eq "P") { $phase="Z"; } 
         if ($phase eq "S") { $phase="s"; }
         $qual=convertqual($deltime);
	 $chan=substr($chan,0,2);

	 $ayear = epoch2str($arvtime, "%Y"); $ayear=substr($ayear,2,2);
         $amon = epoch2str($arvtime, "%m");
         $aday = epoch2str($arvtime, "%d");
         $ahr = epoch2str($arvtime, "%H");
         $amin = epoch2str($arvtime, "%M");
         $asec = epoch2str($arvtime, "%S.%s");
         $asec = sprintf("%4.2f",$asec); $asec=$asec*100;

         if ($phase2 eq "S") { $phase2="s"; }
         $squal=convertqual($deltime2);
         $shr = epoch2str($arvtime2, "%H");
         $smin = epoch2str($arvtime2, "%M");
         $ssec = epoch2str($arvtime2, "%S.%s");
         if ($shr != $ahr && $evid1 == $evid2) { print OUTPUT "$sta1 Problem with hours\n"; next ILOOP; }
	 if ($smin >= $amin ) { $diff=($smin-$amin)*60.0; $ssec=$ssec+$diff; }
         $ssec = sprintf("%4.2f",$ssec); $ssec=$ssec*100;

	 if ($sta1 eq $sta2 && $phase eq "Z" && $phase2 eq "s" ) { 

	         printf OUTPUT ("%-4s %1s %1s %2d%2d%2d%2d%2d %4d        %4d %1s %1d                  %2s 0\n", 
			$sta1, $phase, $qual, $ayear,$amon,$aday,$ahr,$amin,$asec,$ssec,$phase2,$squal,$chan);
		 $i=$j; 
		 $oldevid=$evid1;


	} elsif ( $sta1 ne $sta2 && $phase eq "Z") { 
		printf OUTPUT ("%-4s %1s %1s %2d%2d%2d%2d%2d %4d                                  %2s 0\n",
                        $sta1, $phase, $qual, $ayear,$amon,$aday,$ahr,$amin,$asec,$chan);
                $oldevid=$evid1;

	} elsif ( $sta1 ne $sta2 && $phase eq "s" ) { 
		printf OUTPUT ("%-4s     %2d%2d%2d%2d%2d             %4d %1s %1d                  %2s 0\n",
                        $sta1, $ayear,$amon,$aday,$ahr,$amin,$asec,$phase,$aqual,$chan);
		$oldevid=$evid1;

	}
 
}   # end of ILOOP loop

print OUTPUT "C*(C) SMU catalog last accessed Nov. 2016\n                 1010.00\n";

close(FILE);
close(OUTPUT);
          
sub convertqual { 

	my $deltime=@_[0];
        my $qual=1; 

	if ( $deltime==0.010 ) { 
		$qual=0;
	} elsif ( $deltime==0.020) { 
		$qual=1; 
	} elsif ( $deltime==0.050) { 
		$qual=2; 
	} elsif ( $deltime==0.100 ) {
		$qual==3;
	}

	return $qual;
}
