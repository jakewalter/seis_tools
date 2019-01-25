#!/usr/bin/perl


$i = 2008122;
$max = 2008152;
$f = 20080501;
$fmax = 20080531;
while ($i <= $max) {
@num = $i;

system("ls $f*e6073*.sac > $i");
$i++;
$f++;
}

