#!/usr/bin/perl -w
# getmedian.pl
# get median from stdin and compute its ave.
use POSIX qw(ceil floor);

@stdins = <>;

my @array = @stdins;

my $count = $#array + 1; 
@array = sort { $a <=> $b } @array; 
my $median;
if ($count % 2) {  
	my $index = floor($count/2);
	$median = $array[$index]; 
} else {  
	$median = ($array[$count/2] + $array[$count/2 - 1]) / 2; 
}

chomp($median);
print "$median $count\n";
