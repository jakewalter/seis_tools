#!/usr/bin/env perl

#Pull data from Antelope in 2 hour segments, open sac, stack the data and smooth/filter, ps the files for comparison


# First specify the list of dates
open(TABLEA,"table_test");
open(OUT,">NOT_FOUND");
@tablea = <TABLEA>;

#Directories	
$homeD = "/auto/proj/jwalter/tremor";
$homeD2 = "/auto/proj/jwalter/tremor/test";
$dataDir = "/auto/proj/tremor/tremor07db/SEEDVOLUMES/data_files_archive1";
$i = 0;

while ($i < @tablea) {
   chomp ($tablea[$i]);
   ($date,$time) = (split /\s+/,$tablea[$i])[0,1];
   ($year,$mon,$day) = (split /\//,$date)[0,1,2];
   ($yr) = substr($year,2,2);
   ($hr) = substr($time,0,2);
 
   # find the julian day associate with this date
   system("julday $mon $day $year > temp");

   open(TABLEB,"temp");
   @tableb = <TABLEB>;
   chomp ($tableb[2]);
   ($julday) = (split /\s+/,$tableb[2])[3];
   
   open(TABLEC,"stationlist");
   @tablec = <TABLEC>;
   for ($j = 0; $j < @tablec; $j++) {
         chomp ($tablec[$j]);
         ($sta) = (split /\s+/,$tablec[$j])[0];
     }

   $drct = $dataDir ."/". $sta;   #$year . "." . $julday; 
   close(TABLEB);
   unlink("temp");

   # if corresponding data directory exists - get data for BB stations and put in local
   # directory we create below
   if (-e $drct) { 
      # make a local directory for the data 
      chdir $homeD;
      $etName = $homeD . "/" . $yr . $mon . $day . $hr;
      system("mkdir $etName");
      #system("chmod 775 $etName");
      print "$etName.\n";
      print "$hr.\n";
      system("cp getKZTIMES.csh FIX_HEADERS.perl fillHeadersEVT.csh $etName");
      system("cp stationlist $etName");
      open(TABLEC,"stationlist");
      @tablec = <TABLEC>;
      chdir $drct;

      
      
      for ($j = 0; $j < @tablec; $j++) {
         chomp ($tablec[$j]);
         ($sta) = (split /\s+/,$tablec[$j])[0];

         $checkSta = $sta . ".YQ.01.SHZ." . $year . "." . $julday;
         # if station data exists, copy data to the PP directory (under event folder) 

         if (-e $checkSta) {
           system("cp $sta.".YQ.01.SH*" $homeD2");#$etName
           
           chdir $etName;
           # Convert the data to SAC format 
           system("ms2sac -G 100000000 $sta.*SHE* > $sta.SHE");
           system("ms2sac -G 100000000 $sta.*SHN* > $sta.SHN");
           system("ms2sac -G 100000000 $sta.*SHZ* > $sta.SHZ");
           system("/bin/rm $sta.XY*"); 

           # Now, go through steps to cut and fix data up
           system("getKZTIMES.csh $sta.SHE $sta.SHN $sta.SHZ $etName");
           system("FIX_HEADERS.perl $time $lat $lon $depth");
           unlink("kztimes");
           chdir $drct;
         }
      }
      close(TABLEC);
      unlink("stationList");
      chdir $etName;
      system("/bin/rm getKZTIMES.csh FIX_HEADERS.perl fillHeadersEVT.csh");
      chdir $homeD;

   } else {
      # report as not being found
      print OUT ($drct,"\n");
   } 

   $i = $i + 1;
}











#$program = "sac";
	#$arg1 = "r $hours.\n";
	#$arg2 = "p1";
	#$arg3 = "bd sgf";
	#$arg4 = "p1";


#for ($hours = 24; 
	#--$hours;

	#system ($program, $arg1
	#); 
	#system ($arg1); 
	#system ($arg2); 
	#$arg3, $arg4)



#)

