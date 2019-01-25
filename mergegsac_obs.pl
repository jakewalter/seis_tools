#!/usr/bin/perl -w


#$dir1 = "/auto/proj/nicoya/OBS";
$dir2 = "/auto/proj/jwalter2/obs";

$i = 122;
$imax = 165;
while ($i <= $imax) {

$h = 1;
$hmax = 16;
while ($h <= $hmax) {

$g = 1;
$gmax = 3;
while ($g <= $gmax) {

$sta = sprintf("%02d",$h);
$folder = "2000." . $i;
$last = $sta . "." . $g . ".sac";
$newfile = "2000" . $i . "." . $sta . "." . $g . ".sac";

print "Now making: $newfile \n";
`gsac << END
r $folder/*$i*$last
rmean
merge
w $dir2/$newfile
quit
END
`;
#system("sactosac $newfile");

$g = $g + 1;
}
$h = $h + 1;
}
$i = $i + 1;
}
