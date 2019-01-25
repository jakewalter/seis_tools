#!/usr/bin/perl -w
	# See ~/ant08/fixgaps.m for the other half
	# Run fixgaps.m in matlab, hk2sacbatch.pl in directory, and then this, fixgaps.pl
$filesreside = '/auto/proj/jwalter/ant08/all/all/time/fix/';
#$newdir = '/auto/proj/jwalter/ant08/all/all/time/fix/';

@stalist = ('6127', '6094');
$i = 0;
while ($i < @stalist) {
system("ls *$stalist[$i]*.sac > templistfix");

open(TABLEB,"templistfix");
@tableb = <TABLEB>;
$f = 0;
while ($f < @tableb) {
#system("../$tableb[$f] $tableb[$f]");
`sac << END
r ../$tableb[$f] 
r more $tableb[$f]
copyhdr from 1 nzyear nzjday nzhour nzmin nzsec nzmsec b e kstnm cmpaz cmpinc
ch lovrok
wh
w over
quit
END
`;
$f = $f + 1;
}
$i = $i + 1;
}
close(TABLEB);
