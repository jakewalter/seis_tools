#!/usr/bin/perl -w

`ls */*901* > F2`;

open(TABLEA,"F2");
@tablea = <TABLEA>;

$i = 0;
while ($i < @tablea) {
chomp (@tablea[$i]);
($sta1,$file1) = split '/', $tablea[$i];
($sta,$net,$blank,$nines,$year,$day) = split "\\.", $file1;
$nowfile = $sta1 . '/' . $sta . '.' . $net . '..VM1.' . $year . '.' . $day;
print "$sta1 $file1\n";
system("cp $sta1/$file1 $nowfile");
$i = $i + 1;
}
close(TABLEA);
