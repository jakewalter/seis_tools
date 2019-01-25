#Script to convert multiple gcf files to sac
#Jake Walter - September, 2007


$files = "/auto/proj/jwalter/ardobore";
$put = "/auto/proj/jwalter/ardobore/sac";

open(TABLEA,"$files/gcflist");
@tablea = <TABLEA>;

$i = 0;
while ($i < @tablea) { 
      chomp (@tablea[$i]);
      system ("gcf/bin/gcfconv -S < @tablea[$i] -l 3600 -f "sac" -d $put");
print OUT (@tablea[$i],"\n");
$i = $i + 1;

}
