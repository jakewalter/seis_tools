#!/usr/bin/perl -w



`ls *SAC > F2`;


open(TABLEA,"F2");
@tablea = <TABLEA>;

$i = 0;
while ($i < @tablea) {
$newname = $tablea[$i] . '_deconv'; 
print("$tablea[$i]");
`sac << END
r $tablea[$i]
transfer from evalresp
bp c .02 .05 p 2
interpolate delta 1.0
w $newname
quit
END
`;

	


$i = $i + 1;
}

close(TABLEA);
