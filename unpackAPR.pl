#Script to unpack tarred files and send them to different database, using list of filenames
#Jake Walter - August, 2007


$download = "/auto/proj/jwalter/Hinet_download";
$put = "/auto/proj/Hinet_tremor/APR04_SHIK";

open(TABLEA,"$download/APR04_SHIK");
@tablea = <TABLEA>;

$i = 0;
while ($i < @tablea) { 
      chomp (@tablea[$i]);
      system ("tar -xvf @tablea[$i] -C $put");
print OUT (@tablea[$i],"\n");
$i = $i + 1;

}
