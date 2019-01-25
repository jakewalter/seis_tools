#!/usr/bin/perl -w


#open(MYFILE,">>dayslist");
#print MYFILE "$i.sac\n";
#close(MYFILE);
#system("ls *$i.sac > $i");


#$files = "/auto/proj/jwalter/ant08/all";
#$put = "/auto/proj/jwalter/ant08/all/all";
$f = 325;
$fmax = 344;
$year = 2008;

while ($f <= $fmax) {

$chan = 3;
$stalist = ('QSPA.20.BHE');
$sta = 'QSPA';
#$chanmax = 6;

#while ($chan <= $chanmax) { 
#`ls -1 $files/*$f*1_$i.sac > $files/scratch_mergegsac`;



#pen(TABLEA,"$files/scratch_mergegsac");
#@tablea = <TABLEA>;
      #chomp ($tablea[$i]);
	#($field1,$field2,$field3,$field4,$field5,$field6,$name) = split '/', $tablea[1];
	#($file1,$sac) = split "\\.", $name;
	#$day = substr $file1, 0, 7;
	#$sta = substr $file1, 16, 4;
	#$chan = substr $file1, 23, 1;
	#(,$min,$sta,$blah,$ochan) = split 's//_/', $file1;
	#$names = $day . '_' . $sta . '_' . $chan . '.sac';
	
	
	$loc = $year . $f . '_' . $sta . '_' . $chan . '.sac';
	$stat = $year . '.' . $f;
	#system();
	`gsac << END
	r $stat*$stalist*.SAC
	merge
	w $loc
	quit
	END
	`;

#$chan = $chan + 1;
#}
$f = $f + 1;
}

#close(TABLEA);

$f2 = 20081201;
$fmax2 = 20081215;

while ($f2 <= $fmax2) {



	
	$loc = $f2 . '_' . $stalist . '_' . $chan . '.sac';
	#system();
	`gsac << END
	r $f2*.sac
	merge
	w $loc
	quit
	END
	`;

#$chan = $chan + 1;
#}
$f2 = $f2 + 1;
}

#'cp *$stalist_?.sac $put';
