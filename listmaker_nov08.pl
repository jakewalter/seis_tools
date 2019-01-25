#!/usr/bin/perl


$i = 2008320;
$max = 2008335;
$f = 20081115;
$fmax = 20081130;
while ($i <= $max) {
@num = $i;

system("ls 0003*$i*3.sac 0003*$f*3.sac > $i");
$i++;
$f++;
}

