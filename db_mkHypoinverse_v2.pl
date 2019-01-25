#! /usr/bin/env perl
#-----------------------
# db_mkHypoinverse_v2.pl
# Antelope database perl script
#
# Produces a phase pickfile for hypoinverse
# from an Antelope CSS 3.0 database
#
# you must have perl package "Datascope.pm"
# the "use lib" line points to where antelope keeps it
#
# USAGE: db_mkHypoinverse_v2.pl my_database phasefilename
# Database must contain 'origin', 'assoc', and 'arrival' tables
# OUTPUT: file "hdd_picks.dat" 

use lib "$ENV{ANTELOPE}/data/perl/";
use Datascope;

$dbname = $ARGV[0];
$outfile = 'hypoinv.pha';
open(FILEOUT, ">" , $outfile)  or die "Can't open $outfile: $!";

print "Reading database: $dbname\n";
@db = dbopen("$dbname", "r");
@dbo = dblookup(@db, "" , "origin" , "", "" );
#@dbo = dbsubset(@dbo, "origin.nass >= 3 ");
#@dbo = dbsubset(@dbo, "origin.nass <= 8 ");
#@dbo = dbsubset(@dbo, "orid>=1955");
@dbe = @dbo;
$nrecords = dbquery(@dbo, "dbRECORD_COUNT");
print "$nrecords!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!";
$err = 0.000;
$rms = 0.00;


print "Wrote hypoinverse pickfile: $outfile\n"

