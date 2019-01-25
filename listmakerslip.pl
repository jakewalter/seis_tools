#!/usr/bin/perl


$i = 1;
$max = 32;
while ($i <= $max) {
$name = 'sliplist_' . $i;
$name2 = '3.sact_slip' . $i . '_a';
system("ls *$name2 > $name");
$i++;
}

