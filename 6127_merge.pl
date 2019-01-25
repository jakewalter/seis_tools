#!/usr/bin/perl
#@directories = <6127n2 6127z2 6127e2 6295e2 6295n2 6295z2>;
#$k = 1;
#$max = 6;
#while ($k <= $max) {

#`ls -1 $directories[$k]/200712*sac > F2`;

open(FILENAMES,'F');

$fn0='MergedFiles';

$firstfileflag=0;
while (<FILENAMES>)
  {chomp;
   $fn=$_;

   if ($firstflag==0){
     `cp $fn MergedFiles`;
     $firstflag=1;}

`sac << END
r $fn0
merge $fn
synch
w $fn0
quit
END
`;
}
#system("cp MergedFiles ./all/$directories[$k]");
close(FILENAMES);

#print("$directories[$k]");
#$k++;
#}
#r more $fn
#synch
#w temp1 temp2
#r temp1
