#!/usr/bin/perl


$i = 2008153;
$max = 2008182;
$f = 20080601;
$fmax = 20080630;
while ($i <= $max) {
@num = $i;

system("ls $f*e6073*.sac > $i");
$i++;
$f++;
}

