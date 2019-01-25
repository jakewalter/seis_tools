#!/usr/bin/perl


$i = 2008336;
$max = 2008349;
$f = 20081201;
$fmax = 20081214;
while ($i <= $max) {
@num = $i;

system("ls 0003*$i*3.sac 0003*$f*3.sac > $i");
$i++;
$f++;
}

