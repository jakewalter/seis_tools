#!/usr/bin/perl
#
# do cross-correlation between events for the same station.
#
# Lupei Zhu, 07/08/04, SLU
# 	03/20/08	revise to allow use multiple stations
#	06/21/09	add -B option to do cc between stations

$cmd = "scc";
$cat = "";
$sep = 0.5;		# max. separation in degrees between events
$betwStations = 0;	# do cc between events
# command line options
@ARGV > 0 or die "Usage: crscrl.pl [-Acmd ($cmd)] [-Ecatalog[/max_sep_in_deg ($sep)]] [-Betweentation (between events)] [other options for scc or src_ss]
	and input (event/station ref_time on_or_off) from stdin\n";
foreach (grep(/^-/,@ARGV)) {
   my $opt = substr($_,1,1);
   my @value = split(/\//,substr($_,2));
   if ($opt eq "A") {
     $cmd = $value[0];
   } elsif ($opt eq "B") {
     $betwStations = 1;
   } elsif ($opt eq "E") {
     $cat = $value[0];
     $sep = $value[1] if $#value > 0;
   } elsif ($opt eq "V") {
     $verbose = 1;
   } else {
     $cmd = "$cmd $_";
   }
}
print STDERR "$cmd\n";

# input event locations from the catalog
$col = 2; $col = 1 if $betwStations;
if ($cat && open(AAA,$cat)) {
   while(<AAA>) {
     @aa = split;
     $eve = $aa[0];
     $evla{$eve}=$aa[$col];
     $evlo{$eve}=$aa[$col+1];
   }
   close(AAA);
} else {
   $cat="";
}

# input arrival time data
while (<STDIN>) {
     @aa = split(/[\/\s]+/,$_);
     next if $aa[3]==0;
     $arr{$aa[1]}->{$aa[0]} = $aa[2];
}

# do cross-correlations
foreach $stn (keys(%arr)) {
@all = keys(%{$arr{$stn}});
while ($master=pop(@all)) {
     open(AAA,"| $cmd >> junk.$$");
     $trace = "$master/$stn"; $trace = "$stn/$master" if $betwStations;
     print AAA "$trace $arr{$stn}{$master} 1\n";
     foreach $oth (@all) {
       $trace = "$oth/$stn"; $trace = "$stn/$oth" if $betwStations;
       print AAA "$trace $arr{$stn}{$oth} 1\n" if $cat eq "" or ($cat and
		abs($evla{$master}-$evla{$oth})<$sep and
		abs($evlo{$master}-$evlo{$oth})<$sep );
     }
     close(AAA);
}

# output
open(AAA,"junk.$$");
while(<AAA>) {
     chop;
     @aa=split;
     if ($#aa == 2) {
	$master = $_;
     } else {
	print "$master $_\n";
     }
}
close(AAA);
unlink("junk.$$");
}
