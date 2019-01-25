#!/usr/bin/perl
# convert waveform cc results to DD input format

while (<>) {
  ($eve1a,$sta,$arr1,$eve2a,$sta1,$arr2,$dist,$timeshift,$cc) = split(/[\/\s]+/,$_);
  ($net,$stan,$comp) = split(/[\.\s]/,$sta1);
  $eve1 = '1' . substr($eve1a,4);
  $eve2 = '1' . substr($eve2a,4);

  #next if $flg eq 0;
  #chop($stan); chop($stan);
  if ($cc < 1) {
  	printf "# $eve1 $eve2 0.0\n";
  	printf "$stan %6.2f $cc P\n",$arr1-$arr2;
  }
}
