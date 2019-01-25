#!/usr/bin/perl -w


#open(MYFILE,">>dayslist");
#print MYFILE "$i.sac\n";
#close(MYFILE);
#system("ls *$i.sac > $i");


#$files = "/auto/proj/jwalter/ant08/all";
$put = "/auto/proj/jwalter/ant08/all/all";
$f = 2008203;
$fmax = 2008216;

while ($f <= $fmax) {

$chan = 1;
$chanmax = 6;

while ($chan <= $chanmax) { 
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
	@stalist = ('a703', 'a702');
	$k = 0;
	$kmax = 2;
	while ($k <= $kmax) {
	$loc = $f . '_' . $stalist[$k] . '_' . $chan . '.sac';
	#system();
	`gsac << END
	r $f*$stalist[$k]_1_$chan.sac
	merge
	w $loc
	quit
	END365
	`;
	$k = $k + 1;
}
$chan = $chan + 1;
}
$f = $f + 1;
}

#close(TABLEA);
