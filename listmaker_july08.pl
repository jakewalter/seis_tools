#!/usr/bin/perl


$i = 2008183;
$max = 2008213;
$f = 20080701;
$fmax = 20080731;
while ($i <= $max) {
@num = $i;

system("ls $f*e6073*.sac > $i");
$i++;
$f++;
}

