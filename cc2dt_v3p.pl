#!/usr/bin/perl
# convert waveform cc results to DD input format

while (<>) {
  ($dir1,$eve1a,$sta,$arr1,$dir2,$eve2a,$sta1,$arr2,$dist,$timeshift,$cc) = split(/[\/\s]+/,$_);
  #($eve1dir,$blah,$eve2dir) = split(/[\ \s]/,$_);
  ($net,$stan,$comp) = split(/[\.\s]/,$sta1);
  #$eve1 = '1' . substr($eve1a,4);
  #$eve2 = '1' . substr($eve2a,4);
  $eve1 = `cat $dir1/$eve1a/origid.dat`;
  $eve2 = `cat $dir2/$eve2a/origid.dat`;
  chomp($eve1); chomp($eve2); #print "$eve1\n";
  #if eve1
  #next if $flg eq 0;
  #chop($stan); chop($stan);
  if ($cc < 1) {
	printf "$eve1 $eve2 $stan %.2f $cc P\n",$arr1-$arr2;
	#if ($comp =~ /HE$/) {
  	#	printf "$eve1 $eve2 $stan %.2f $cc S\n",$arr1-$arr2;
	#} elsif ($comp =~ /HN$/) {
	#	printf "$eve1 $eve2 $stan %.2f $cc S\n",$arr1-$arr2;
	#} else {
	#	printf "$eve1 $eve2 $stan %.2f $cc P\n",$arr1-$arr2;
	#}
  }
}
