#!/usr/bin/perl
#
# FetchBulkData
#
# Fetch bulk data from the DMC web interfaces.  This program is
# primarily written to select and fetch waveform data but can also
# fetch metadata and response information.
#
# Dependencies: This script should run without problems on Perl
# release 5.10 or newer, older versions of Perl might require the
# installation of the following modules (and their dependencies):
#   XML::SAX
#   Bundle::LWP (libwww-perl)
#
# Installation of the XML::SAX::ExpatXS module can significantly
# speed up the parsing of metadata results returned as XML.
#
# Data selection
#
# Data is generally selected by specifying network, station, location,
# channel, quality, start time and end time.  The name parameters may
# contain wildcard characters.  All input options are optional but
# waveform requests should include a time window.  Data may be
# selected one of three ways:
#
# 1) Command line arguments: -N, -S, -L, -C, -Q, -s, -e
#
# 2) A selection file containing a list of:
#    Net Sta Loc Chan Start End
#
# 3) A BREQ_FAST formatted file
#
# Data output
#
# miniSEED: If the -o option is used to specify an output file
# waveform data will be requested based on the selection and all
# written to the single file.
#
# metadata: If the -m option is used to specifiy a metadata file a
# line will be written to the file for each channel epoch and will
# contain:
# "net,sta,loc,chan,lat,lon,elev,depth,azimuth,SACdip,instrument,scale,scalefreq,scaleunits,samplerate,start,end"
#
# The dip field in this output will be converted from the SEED to SAC
# convention by adding 90.  This metadata file can be used directly
# with mseed2sac or tracedsp to create SAC files including basic
# metadata.
#
# SAC P&Zs: If the -sd option is given SAC Poles and Zeros will be
# fetched and a file for each channel will be written to the specified
# directory with the name 'SACPZ.Net.Sta.Loc.Chan'.  If this option is
# used while fetching waveform data, only channels which returned
# waveforms will be requested.
#
# RESP: If the -rd option is given SEED RESP (as used by evalresp)
# will be fetched and a file for each channel will be written to the
# specified directory with the name 'RESP.Net.Sta.Loc.Chan'.  If this
# option is used while fetching waveform data, only channels which
# returned waveforms will be requested.
#
#
# ## Change history ##
#
# 2010.140:
#  - Initial version
#
# 2010.148:
#  - Add options to fetch SAC P&Z and RESP data
#  - Make waveform collection optional
#  - Limit metadata channel epochs to be within request window
#  - Print "DONE" to STDERR when finished
#
# 2010.154:
#  - Add -a option to specify authorization credentials
#
# 2010.164:
#  - Add download handler and timer for XML metadata for improved feedback
#  - Use HTTP Keep-Alive connections for waveforms, SACPZs and RESPs
#
# 2010.171:
#  - Add check for start/end times when requesting waveform data
#  - Add fetching timers and rate calculations for improved feedback
#
# 2010.177
#  - Branch from FetchData to use the bulk data selection webservice,
#      reorganize quality to be specified as a global selection in URI.
#
# 2010.180
#  - Change quality designation to go into selection block (POST)
#
# 2010.188
#  - Convert component inclination/dip to SAC convention (+90) when
#  writing metadata to an output file, header field is now "SACdip".
#
# 2010.201
#  - Fix up total download size reporting.
#
# 2010.217
#  - Cleanup some documentation, add warnings about metadata service.
#  - Print "DONE" and "Received ..." output to STDERR for consistency.
#
# 2010.273
#  - Add -A option to specify an application name/version, this will be
#  added to the UserAgent string.
#
# 2010.342
#  - Convert metadata fetching to use the production ws-station service
#  instead of the deprecated service previously used.
#  - Rearrange and add fields to the metadata file output lines.
#
# 2011.020
#  - Rework metadata parser for changed content (InstrumentSensitivity).
#  - Add diagnostics and more graceful failure to metadata retrieval.
#
# 2011.046
#  - Save received XML metadata to a temporary file, the PurePerl SAX
#  XML parser is much faster when working on files.
#  - Allow comma-separated lists for selection by changing the delimiter
#  for selection entries.
#  - Truncate future dates to year 2038 for older versions of HTTP::Date.
#
# 2011.067
#  - Add -msl (minimum segment length) and -lso (longest segment only)
#
# 2011.077
#  - Add undocumented webservice overrides: -msurl, -wsurl, -sacpzurl and -respurl
#
# 2011.089
#  - Fix error message to report unrecognized channels in BREQ_FAST files.
#
# Author: Chad Trabant, IRIS Data Managment Center

use strict;
use File::Basename;
use Getopt::Long;
use LWP::UserAgent;
use HTTP::Status qw(status_message);
use HTTP::Date;
use Time::HiRes;

my $version = "2011.089";

# Web service for metadata
my $metadataservice = 'http://www.iris.edu/ws/station/query';

# Web service for bulk waveform data
my $waveformservice = 'http://www.iris.edu/ws/bulkdataselect/query';

# Web service for SAC P&Z
my $sacpzservice = 'http://www.iris.edu/ws/sacpz/query';

# Web service for RESP
my $respservice = 'http://www.iris.edu/ws/resp/query';

# HTTP UserAgent reported to web services
my $useragent = "FetchBulkData/$version";

my $usage      = undef;
my $verbose    = undef;

my $net        = undef;
my $sta        = undef;
my $loc        = undef;
my $chan       = undef;
my $qual       = "B";
my $starttime  = undef;
my $endtime    = undef;
my $selectfile = undef;
my $bfastfile  = undef;
my $mslopt     = undef;
my $lsoopt     = undef;
my $appname    = undef;
my $auth       = undef;
my $outfile    = undef;
my $sacpzdir   = undef;
my $respdir    = undef;
my $metafile   = undef;

# Parse command line arguments
Getopt::Long::Configure ("bundling_override");
my $getoptsret = GetOptions ( 'help|usage|h'   => \$usage,
                              'verbose|v+'     => \$verbose,
                              'net|N=s'        => \$net,
                              'sta|S=s'        => \$sta,
                              'loc|L=s'        => \$loc,
                              'chan|C=s'       => \$chan,
                              'qual|Q=s'       => \$qual,
			      'starttime|s=s'  => \$starttime,
			      'endtime|e=s'    => \$endtime,
			      'selectfile|l=s' => \$selectfile,
			      'bfastfile|b=s'  => \$bfastfile,
			      'msl=s'          => \$mslopt,
			      'lso'            => \$lsoopt,
			      'appname|A=s'    => \$appname,
			      'auth|a=s'       => \$auth,
			      'outfile|o=s'    => \$outfile,
			      'sacpzdir|sd=s'  => \$sacpzdir,
			      'respdir|rd=s'   => \$respdir,
			      'metafile|m=s'   => \$metafile,
			      'msurl=s'        => \$metadataservice,
			      'wsurl=s'        => \$waveformservice,
			      'sacpzurl=s'     => \$sacpzservice,
			      'respurl=s'      => \$respservice,
			    );

my $required =  ( defined $net || defined $sta ||
		  defined $loc || defined $chan ||
		  defined $starttime || defined $endtime ||
		  defined $selectfile || defined $bfastfile );

if ( ! $getoptsret || $usage || ! $required ) {
  my $script = basename($0);
  print "$script: collect waveform data from the IRIS DMC (version $version)\n\n";
  print "Usage: $script [options]\n\n";
  print " Options:\n";
  print " -v                Increase verbosity, may be specified multiple times\n";
  print " -N,--net          Network code, default is all\n";
  print " -S,--sta          Station code, default is all\n";
  print " -L,--loc          Location ID, default is all\n";
  print " -C,--chan         Channel codes, default is all\n";
  print " -Q,--qual         Quality indicator, default is best\n";
  print " -s starttime      Specify start time (YYYY-MM-DD,HH:MM:SS)\n";
  print " -e endtime        Specify end time (YYYY-MM-DD,HH:MM:SS)\n";
  print " -l listfile       Read list of selections from file\n";
  print " -b bfastfile      Read list of selections from BREQ_FAST file\n";
  print " -msl length       Limit returned data to a minimum segment length (sec)\n";
  print " -lso              Limit returned data to the longest segment only\n";
  print " -A appname        Application/version string for identification\n";
  print " -a user:pass      User and password when authentication is needed\n";
  print "\n";
  print " -o outfile        Fetch waveform data and write to output file\n";
  print " -sd sacpzdir      Fetch SAC P&Zs and write files to sacpzdir\n";
  print " -rd respdir       Fetch RESP and write files to respdir\n";
  print " -m metafile       Write basic metadata to specified file\n";
  print "\n";
  exit 1;
}

# Check for existence of output directories
if ( $sacpzdir && ! -d "$sacpzdir" ) {
  die "Cannot find SAC P&Zs output directory: $sacpzdir\n";
}
if ( $respdir && ! -d "$respdir" ) {
  die "Cannot find RESP output directory: $respdir\n";
}

# Check for time window if requesting waveform data
if ( $outfile && ( ! defined $selectfile && ! defined $bfastfile &&
		   ( ! defined $starttime || ! defined $endtime ) ) ) {
  die "Cannot request waveform data without start and end times\n";
}

# Normalize time strings
if ( $starttime ) {
  my ($year,$month,$mday,$hour,$min,$sec) = split (/[-:,.\s\/T]/, $starttime);
  $starttime = sprintf ("%04d-%02d-%02dT%02d:%02d:%02d", $year, $month, $mday, $hour, $min, $sec);
}

if ( $endtime ) {
  my ($year,$month,$mday,$hour,$min,$sec) = split (/[-:,.\s\/T]/, $endtime);
  $endtime = sprintf ("%04d-%02d-%02dT%02d:%02d:%02d", $year, $month, $mday, $hour, $min, $sec);
}

# An array to hold data selections
my @selections = ();

# Add command line selection to list
if ( defined $net || defined $sta || defined $loc || defined $chan ||
     defined $starttime || defined $endtime ) {
  push (@selections,"$net|$sta|$loc|$chan|$starttime|$endtime");
}

# Read selection list file
if ( $selectfile ) {
  print STDERR "Reading data selection from list file '$selectfile'\n";
  &ReadSelectFile ($selectfile);
}

# Read BREQ_FAST file
if ( $bfastfile ) {
  print STDERR "Reading data selection from BREQ_FAST file '$bfastfile'\n";
  &ReadBFastFile ($bfastfile);
}

# Report complete data selections
if ( $verbose > 2 ) {
  print STDERR "== Data selections ==\n";
  foreach my $select ( @selections ) {
    print STDERR "    $select\n";
  }
}

# An array to hold channel list and metadata
my %request = (); # Value is metadata range for selection
my @metadata = ();
my $metadataxml;

# Fetch metadata from the station web service
foreach my $selection ( @selections ) {
  my ($snet,$ssta,$sloc,$schan,$sstart,$send) = split (/\|/,$selection);
  &FetchMetaData($snet,$ssta,$sloc,$schan,$sstart,$send);
}

# Report complete data requests
if ( $verbose > 2 ) {
  print STDERR "== Request list ==\n";
  foreach my $req ( sort keys %request ) {
    print STDERR "    $req (metadata: $request{$req})\n";
  }
}

# Track bytes downloaded in callback handlers
my $datasize = 0;

# Fetch waveform data if output file specified
&FetchWaveformData() if ( $outfile );

# Collect SAC P&Zs if output directory specified
&FetchSACPZ if ( $sacpzdir );

# Collect RESP if output directory specified
&FetchRESP if ( $respdir );

# Write metadata to file
if ( $metafile ) {
  if ( scalar @metadata <= 0 ) {
    printf STDERR "No metdata available\n", scalar @metadata;
  }
  else {
    printf STDERR "Writing metadata (%d channel epochs) file\n", scalar @metadata if ( $verbose );

    open (META, ">$metafile") || die "Cannot open metadata file '$metafile': $!\n";

    # Print header line
    print META "#net,sta,loc,chan,lat,lon,elev,depth,azimuth,SACdip,instrument,scale,scalefreq,scaleunits,samplerate,start,end\n";

    foreach my $channel ( sort @metadata ) {
      my ($net,$sta,$loc,$chan,$start,$end,$lat,$lon,$elev,$depth,$azimuth,$dip,$instrument,$samplerate,$sens,$sensfreq,$sensunit) =
	split (/,/, $channel);

      # Convert inclination/dip to SAC convention
      $dip += 90;

      $sensfreq = sprintf ("%0g", $sensfreq);
      $samplerate = sprintf ("%0g", $samplerate);

      print META "$net,$sta,$loc,$chan,$lat,$lon,$elev,$depth,$azimuth,$dip,$instrument,$sens,$sensfreq,$sensunit,$samplerate,$start,$end\n";
    }

    close META;
  }
}

print STDERR "DONE\n";
## End of main


######################################################################
# ReadSelectFile:
#
# Read selection list file and add entries to the @selections array.
#
# Selection lines are expected to be in the following form:
#
# "Net Sta Loc Chan Start End"
#
# The Net, Sta, Loc and Channel fields are required and can be
# specified as wildcards.
######################################################################
sub ReadSelectFile {
  my $selectfile = shift;

  open (SF, "<$selectfile") || die "Cannot open '$selectfile': $!\n";

  foreach my $line ( <SF> ) {
    chomp $line;
    next if ( $line =~ /^\#/ ); # Skip comment lines

    my ($net,$sta,$loc,$chan,$start,$end) = split (' ', $line);

    next if ( ! defined $chan );

    # Normalize time strings
    if ( $start ) {
      my ($year,$month,$mday,$hour,$min,$sec) = split (/[-:,.\s\/T]/, $start);
      $start = sprintf ("%04d-%02d-%02dT%02d:%02d:%02d", $year, $month, $mday, $hour, $min, $sec);
    }

    if ( $end ) {
      my ($year,$month,$mday,$hour,$min,$sec) = split (/[-:,.\s\/T]/, $end);
      $end = sprintf ("%04d-%02d-%02dT%02d:%02d:%02d", $year, $month, $mday, $hour, $min, $sec);
    }

    # Add selection to global list
    push (@selections,"$net|$sta|$loc|$chan|$start|$end");
  }

  close SF;
} # End of ReadSelectFile()


######################################################################
# ReadBFastFile:
#
# Read BREQ_FAST file and add entries to the @selections array.
#
######################################################################
sub ReadBFastFile {
  my $bfastfile = shift;

  open (BF, "<$bfastfile") || die "Cannot open '$bfastfile': $!\n";

  my $linecount = 0;
  BFLINE: foreach my $line ( <BF> ) {
    chomp $line;
    $linecount++;
    next if ( ! $line ); # Skip empty lines

    # Capture .QUALTIY header
    if ( $line =~ /^\.QUALITY .*$/ ) {
      ($qual) = $line =~ /^\.QUALITY ([DRQMB])/;
      next;
    }

    next if ( $line =~ /^\./ ); # Skip other header lines

    my ($sta,$net,$syear,$smon,$sday,$shour,$smin,$ssec,$eyear,$emon,$eday,$ehour,$emin,$esec,$count,@chans) = split (' ', $line);

    # Simple validation of BREQ FAST fields
    if ( $sta !~ /^[A-Za-z0-9*?]{1,5}$/ ) {
      print "Unrecognized station code: '$sta', skipping line $linecount\n" if ( $verbose );
      next;
    }
    if ( $net !~ /^[_A-Za-z0-9*?]+$/ ) {
      print "Unrecognized network code: '$net', skipping line $linecount\n" if ( $verbose );
      next;
    }
    if ( $syear !~ /^\d\d\d\d$/ ) {
      print "Unrecognized start year: '$syear', skipping line $linecount\n" if ( $verbose );
      next;
    }
    if ( $smon !~ /^\d{1,2}$/ ) {
      print "Unrecognized start month: '$smon', skipping line $linecount\n" if ( $verbose );
      next;
    }
    if ( $sday !~ /^\d{1,2}$/ ) {
      print "Unrecognized start day: '$sday', skipping line $linecount\n" if ( $verbose );
      next;
    }
    if ( $shour !~ /^\d{1,2}$/ ) {
      print "Unrecognized start hour: '$shour', skipping line $linecount\n" if ( $verbose );
      next;
    }
    if ( $smin !~ /^\d{1,2}$/ ) {
      print "Unrecognized start min: '$smin', skipping line $linecount\n" if ( $verbose );
      next;
    }
    if ( $ssec !~ /^\d{1,2}\.?\d{0,4}?$/ ) {
      print "Unrecognized start seconds: '$ssec', skipping line $linecount\n" if ( $verbose );
      next;
    }
    if ( $eyear !~ /^\d\d\d\d$/ ) {
      print "Unrecognized end year: '$eyear', skipping line $linecount\n" if ( $verbose );
      next;
    }
    if ( $emon !~ /^\d{1,2}$/ ) {
      print "Unrecognized end month: '$emon', skipping line $linecount\n" if ( $verbose );
      next;
    }
    if ( $eday !~ /^\d{1,2}$/ ) {
      print "Unrecognized end day: '$eday', skipping line $linecount\n" if ( $verbose );
      next;
    }
    if ( $ehour !~ /^\d{1,2}$/ ) {
      print "Unrecognized end hour: '$ehour', skipping line $linecount\n" if ( $verbose );
      next;
    }
    if ( $emin !~ /^\d{1,2}$/ ) {
      print "Unrecognized end min: '$emin', skipping line $linecount\n" if ( $verbose );
      next;
    }
    if ( $esec !~ /^\d{1,2}\.?\d?$/ ) {
      print "Unrecognized end seconds: '$esec', skipping line $linecount\n" if ( $verbose );
      next;
    }
    if ( $count !~ /^\d+$/ || $count <= 0 ) {
      print "Invalid channel count field: '$count', skipping line $linecount\n" if ( $verbose );
      next;
    }
    if ( scalar @chans <= 0 ) {
      print "No channels specified, skipping line $linecount\n" if ( $verbose );
      next;
    }

    # Extract location ID if present, i.e. if channel count is one less than present
    my $loc = undef;
    $loc = pop @chans if ( scalar @chans == ($count+1) );

    if ( $loc && $loc !~ /^[A-Za-z0-9*?]{1,2}$/ ) {
      print "Unrecognized location ID: '$loc', skipping line $linecount\n" if ( $verbose );
      next;
    }

    foreach my $chan ( @chans ) {
      if ( $chan !~ /^[A-Za-z0-9*?]{3,3}$/ ) {
	print "Unrecognized channel codes: '$chan', skipping line $linecount\n" if ( $verbose );
	next BFLINE;
      }
    }

    if ( scalar @chans != $count ) {
      printf "Channel count field ($count) does not match number of channels specified (%d), skipping line $linecount\n",
	scalar @chans if ( $verbose );
      next;
    }

    # Normalize time strings
    my $start = sprintf ("%04d-%02d-%02dT%02d:%02d:%02d", $syear, $smon, $sday, $shour, $smin, $ssec);
    my $end = sprintf ("%04d-%02d-%02dT%02d:%02d:%02d", $eyear, $emon, $eday, $ehour, $emin, $esec);

    # Add selection to global list for each channel
    foreach my $chan ( @chans ) {
      push (@selections,"$net|$sta|$loc|$chan|$start|$end");
    }
  }

  close BF;
} # End of ReadBFastFile()


######################################################################
# FetchWaveformData:
#
# Collect waveform data for each entry in the %request hash.  All
# returned data is written to the global output file handle.
#
######################################################################
sub FetchWaveformData {
  # Open output file
  open (OUT, ">$outfile") || die "Cannot open output file '$outfile': $!\n";

  # Create HTTP user agent
  my $ua = RequestAgent->new(keep_alive => 1);

  my $count = 0;

  print STDERR "Fetching waveform data\n" if ( $verbose );
  my $ftime = Time::HiRes::time;
  my $totalbytes = 0;

  # Create web service URI
  my $uri = "${waveformservice}";

  # Create POST data selection: specify options followed by selections
  my $postdata = "quality $qual\n";
  $postdata .= "minimumlength=$mslopt\n" if ( defined $mslopt );
  $postdata .= "longestonly=true\n" if ( defined $lsoopt );

  foreach my $req ( sort keys %request ) {
    my ($wnet,$wsta,$wloc,$wchan,$wstart,$wend) = split (/\|/, $req);
    $count++;

    $postdata .= "$wnet $wsta $wloc $wchan $wstart $wend\n";
  }

  if ( ! $count ) {
    print STDERR "No data selections to request\n";
    return;
  }

  print STDERR "Waveform URI: '$uri'\n" if ( $verbose > 1 );
  print STDERR "Data selection (POST):\n$postdata" if ( $verbose > 1 );

  print STDERR "Downloading waveform data ($count selections) :: Received " if ( $verbose );

  $datasize = 0;

  # Fetch waveform data from web service using callback routine
  my $response = $ua->post($uri, Content => $postdata, ':content_cb' => \&DLCallBack );

  if ( $response->code == 404 ) {
    print STDERR "\b\b\b\b\b\b\b\b\bNo data available\n" if ( $verbose );
  }
  elsif ( ! $response->is_success() ) {
    print STDERR "\b\b\b\b\b\b\b\b\bError fetching data: "
      . $response->code . " :: " . status_message($response->code) . "\n";
    print STDERR "  URI: '$uri'\n" if ( $verbose > 1 );
  }
  else {
    print STDERR "\n" if ( $verbose );
  }

  close OUT;

  my $duration = Time::HiRes::time - $ftime;
  my $rate = $datasize/(($duration)?$duration:0.000001);
  printf (STDERR "Received %s of waveform data in %.1f seconds (%s/s)\n",
	  sizestring($datasize), $duration, sizestring($rate));

  # Remove empty file
  unlink $outfile if ( -z $outfile );
} # End of FetchWaveformData


######################################################################
# FetchSACPZ:
#
# Fetch SAC Poles and Zeros for each entry in the %request hash with a
# defined value.  The result for each channel is written to a separate
# file in the specified directory.
#
######################################################################
sub FetchSACPZ {
  # Create HTTP user agent
  my $ua = RequestAgent->new(keep_alive => 1);

  my $count = 0;
  my $total = 0;
  foreach my $req ( keys %request ) { $total++ if ( defined $request{$req} ); }

  print STDERR "Fetching SAC Poles and Zeros\n" if ( $verbose );
  my $ftime = Time::HiRes::time;
  my $totalbytes = 0;

  foreach my $req ( sort keys %request ) {
    # Skip entries with values not set to 1, perhaps no data was fetched
    next if ( ! defined $request{$req} );

    my ($rnet,$rsta,$rloc,$rchan,$rstart,$rend) = split (/\|/, $req);
    my ($mstart,$mend) = split (/\|/, $request{$req});
    $count++;

    # Generate output file name and open
    my $sacpzfile = "$sacpzdir/SACPZ.$rnet.$rsta.$rloc.$rchan";
    if ( ! open (OUT, ">$sacpzfile") ) {
      print STDERR "Cannot open output file '$sacpzfile': $!\n";
      next;
    }

    # Use metadata start and end if not specified
    $rstart = $mstart if ( ! $rstart );
    $rend = $mend if ( ! $rend );

    # Create web service URI
    my $uri = "${sacpzservice}?net=$rnet&sta=$rsta&loc=$rloc&cha=$rchan";
    $uri .= "&starttime=$rstart" if ( $rstart );
    $uri .= "&endtime=$rend" if ( $rend );

    print STDERR "SAC-PZ URI: '$uri'\n" if ( $verbose > 1 );

    print STDERR "Downloading $sacpzfile ($count/$total) :: Received " if ( $verbose );

    $datasize = 0;

    # Fetch data from web service using callback routine
    my $response = $ua->get($uri, ':content_cb' => \&DLCallBack );

    if ( $response->code == 404 ) {
      print STDERR "\b\b\b\b\b\b\b\b\bNo data available\n" if ( $verbose );
    }
    elsif ( ! $response->is_success() ) {
      print STDERR "\b\b\b\b\b\b\b\b\bError fetching data: "
	. $response->code . " :: " . status_message($response->code) . "\n";
      print STDERR "  URI: '$uri'\n" if ( $verbose > 1 );
    }
    else {
      print STDERR "\n" if ( $verbose );
    }

    # Add data bytes to global total
    $totalbytes += $datasize;

    close OUT;

    # Remove file if no data was fetched
    unlink $sacpzfile if ( $datasize == 0 );
  }

  my $duration = Time::HiRes::time - $ftime;
  my $rate = $totalbytes/(($duration)?$duration:0.000001);
  printf (STDERR "Received %s of SAC P&Zs in %.1f seconds (%s/s)\n",
	  sizestring($totalbytes), $duration, sizestring($rate));

} # End of FetchSACPZ


######################################################################
# FetchRESP:
#
# Fetch SEED RESP for each entry in the %request hash with a value of
# 1.  The result for each channel is written to a separate file in the
# specified directory.
#
######################################################################
sub FetchRESP {
  # Create HTTP user agent
  my $ua = RequestAgent->new(keep_alive => 1);

  my $count = 0;
  my $total = 0;
  foreach my $req ( keys %request ) { $total++ if ( defined $request{$req} ); }

  print STDERR "Fetching RESP\n" if ( $verbose );
  my $ftime = Time::HiRes::time;
  my $totalbytes = 0;

  foreach my $req ( sort keys %request ) {
    # Skip entries with values not set to 1, perhaps no data was fetched
    next if ( ! defined $request{$req} );

    my ($rnet,$rsta,$rloc,$rchan,$rstart,$rend) = split (/\|/, $req);
    my ($mstart,$mend) = split (/\|/, $request{$req});
    $count++;

    # Translate metadata location ID from "--" to blank
    my $ploc = ( $loc eq "--" ) ? "" : $loc;

    # Generate output file name and open
    my $respfile = "$respdir/RESP.$rnet.$rsta.$ploc.$rchan";
    if ( ! open (OUT, ">$respfile") ) {
      print STDERR "Cannot open output file '$respfile': $!\n";
      next;
    }

    # Use metadata start and end if not specified
    $rstart = $mstart if ( ! $rstart );
    $rend = $mend if ( ! $rend );

    # Create web service URI
    my $uri = "${respservice}?net=$rnet&sta=$rsta&loc=$rloc&cha=$rchan";
    $uri .= "&starttime=$rstart" if ( $rstart );
    $uri .= "&endtime=$rend" if ( $rend );

    print STDERR "RESP URI: '$uri'\n" if ( $verbose > 1 );

    print STDERR "Downloading $respfile ($count/$total) :: Received " if ( $verbose );

    $datasize = 0;

    # Fetch data from web service using callback routine
    my $response = $ua->get($uri, ':content_cb' => \&DLCallBack );

    if ( $response->code == 404 ) {
      print STDERR "\b\b\b\b\b\b\b\b\bNo data available\n" if ( $verbose );
    }
    elsif ( ! $response->is_success() ) {
      print STDERR "\b\b\b\b\b\b\b\b\bError fetching data: "
	. $response->code . " :: " . status_message($response->code) . "\n";
      print STDERR "  URI: '$uri'\n" if ( $verbose > 1 );
    }
    else {
      print STDERR "\n" if ( $verbose );
    }

    # Add data bytes to global total
    $totalbytes += $datasize;

    close OUT;

    # Remove file if no data was fetched
    unlink $respfile if ( $datasize == 0 );
  }

  my $duration = Time::HiRes::time - $ftime;
  my $rate = $totalbytes/(($duration)?$duration:0.000001);
  printf (STDERR "Received %s of RESP in %.1f seconds (%s/s)\n",
	  sizestring($totalbytes), $duration, sizestring($rate));

} # End of FetchRESP


######################################################################
# DLCallBack:
#
# A call back for LWP downloading.
#
# Write received data to output file, tally up the received data size
# and print and updated (overwriting) byte count string.
######################################################################
sub DLCallBack {
  my ($data, $response, $protocol) = @_;
  print OUT $data;
  $datasize += length($data);

  if ( $verbose ) {
    printf (STDERR " %-10.10s\b\b\b\b\b\b\b\b\b\b\b", sizestring($datasize));
  }
}


######################################################################
# FetchMetaData:
#
# Collect metadata and expand wildcards for selected data set.
#
# Resulting metadata is placed in the global @metadata array with each
# entry taking the following form:
#   "net,sta,loc,chan,start,end,lat,lon,elev,depth,azimuth,dip,instrument,samplerate,sensitivity,sensfreq,sensunits"
#
# In addition, an entry for the unique NSLCQ time-window is added to
# the %request hash, used later to request data.  The value of the
# request hash entries is maintained to be the range of Channel epochs
# that match the time selection.
#
######################################################################
sub FetchMetaData {
  my ($rnet,$rsta,$rloc,$rchan,$rstart,$rend) = @_;

  # Create HTTP user agent
  my $ua = RequestAgent->new();

  # Convert request start/end times to epoch times
  my $rstartepoch = str2time ($rstart);
  my $rendepoch = str2time ($rend);

  # Create web service URI
  my $uri = "${metadataservice}?level=chan";
  $uri .= "&network=$rnet" if ( $rnet );
  $uri .= "&station=$rsta" if ( $rsta );
  $uri .= "&location=$rloc" if ( $rloc );
  $uri .= "&channel=$rchan" if ( $rchan );
  if ( $rstart && $rend ) {
    my ($startdate) = $rstart =~ /^(\d{4,4}-\d{1,2}-\d{1,2}).*$/;
    my ($enddate) = $rend =~ /^(\d{4,4}-\d{1,2}-\d{1,2}).*$/;

    $uri .= "&timewindow=${startdate},${enddate}";
  }

  my $ftime = Time::HiRes::time;

  print STDERR "Metadata URI: '$uri'\n" if ( $verbose > 1 );

  print STDERR "Fetching metadata :: Received " if ( $verbose );

  $datasize = 0;
  $metadataxml = "";

  # Fetch metadata from web service using callback routine
  my $response = $ua->get($uri, ':content_cb' => \&MDCallBack );

  if ( $response->code == 404 ) {
    print STDERR "\b\b\b\b\b\b\b\b\bNo data available\n" if ( $verbose );
    return;
  }
  elsif ( ! $response->is_success() ) {
    print STDERR "\b\b\b\b\b\b\b\b\bError fetching data: "
      . $response->code . " :: " . status_message($response->code) . "\n";
    print STDERR "  URI: '$uri'\n" if ( $verbose > 1 );
  }
  else {
    print STDERR "\n" if ( $verbose );
  }

  my $duration = Time::HiRes::time - $ftime;
  my $rate = $datasize/(($duration)?$duration:0.000001);
  printf (STDERR "Received %s of metadata in %.1f seconds (%s/s)\n",
	  sizestring($datasize), $duration, sizestring($rate));

  # Return if no metadata received
  return if ( length $metadataxml <= 0 );

  # Create stream oriented XML parser instance
  use XML::SAX;
  my $parser = new XML::SAX::ParserFactory->parser( Handler => MDSHandler->new );

  my $totalepochs = 0;

  my $ptime = Time::HiRes::time;

  print STDERR "Parsing XML metadata... " if ( $verbose );

  # Open file to store metadata XML
  my $metadataxmlfile = "metadata-$$.xml";
  if ( open (MXML, ">$metadataxmlfile") ) {
    # Write XML and close file
    print MXML $metadataxml;
    close MXML;

    # Parse XML metadata from file
    $parser->parse_file ($metadataxmlfile);

    # Remove temporary XML metadata file
    if ( ! unlink $metadataxmlfile ) {
      print STDERR "Cannot remove temporary XML metadata file: $!\n";
    }
  }
  # Otherwise parse the XML in memory
  else {
    printf STDERR " in memory (possibly slow), " if ( $verbose );

    # Parse XML metadata from string
    $parser->parse_string ($metadataxml);
  }

  printf STDERR "Done (%.1f seconds)\n", Time::HiRes::time - $ptime if ( $verbose );

  my $duration = Time::HiRes::time - $ftime;
  my $rate = $datasize/(($duration)?$duration:0.000001);
  printf (STDERR "Processed metadata for $totalepochs channel epochs in %.1f seconds (%s/s)\n",
	  $duration, sizestring($rate));

  ## End of this routine, below is the XML parsing handler used above

  ## Beginning of SAX MDSHandler, event-based streaming XML parsing
  package MDSHandler;
  use base qw(XML::SAX::Base);
  use HTTP::Date;

  my $inepoch = 0;
  my $instart = 0;
  my $inend = 0;
  my $inlat = 0;
  my $inlat = 0;
  my $inlon = 0;
  my $inelevation = 0;
  my $indepth = 0;
  my $inazimuth = 0;
  my $indip = 0;
  my $insamplerate = 0;
  my $inequiptype = 0;

  my $intotalsens = 0;
  my $insensvalue = 0;
  my $insensunits = 0;
  my $infrequency = 0;

  my ($net,$sta,$loc,$chan,$start,$end,$lat,$lon,$elev,$depth,$azimuth,$dip,$instrument,$samplerate,$sens,$sensfreq,$sensunit) = (undef) x 17;

  sub start_element {
    my ($self,$element) = @_;

    if ( $element->{Name} eq "Station" ) {
      ($net,$sta,$loc,$chan,$start,$end,$lat,$lon,$elev,$depth,$azimuth,$dip,$instrument,$samplerate,$sens,$sensfreq,$sensunit) = (undef) x 17;

      $net = $element->{Attributes}->{'{}net_code'}->{Value};
      $sta = $element->{Attributes}->{'{}sta_code'}->{Value};
    }

    elsif ( $element->{Name} eq "Channel" ) {
      $loc = $element->{Attributes}->{'{}loc_code'}->{Value};
      $chan = $element->{Attributes}->{'{}chan_code'}->{Value};
    }

    elsif ( $element->{Name} eq "Epoch" ) {
      $inepoch = 1;
    }

    if ( $inepoch ) {
      if ( $element->{Name} eq "StartDate" ) { $instart = 1; }
      elsif ( $element->{Name} eq "EndDate" ) { $inend = 1; }
      elsif ( $element->{Name} eq "Lat" ) { $inlat = 1; }
      elsif ( $element->{Name} eq "Lon" ) { $inlon = 1; }
      elsif ( $element->{Name} eq "Elevation" ) { $inelevation = 1; }
      elsif ( $element->{Name} eq "Depth" ) { $indepth = 1; }
      elsif ( $element->{Name} eq "Azimuth" ) { $inazimuth = 1; }
      elsif ( $element->{Name} eq "Dip" ) { $indip = 1; }
      elsif ( $element->{Name} eq "SampleRate" ) { $insamplerate = 1; }

      elsif ( $element->{Name} eq "EquipType" ) { $inequiptype = 1; }

      elsif ( $element->{Name} eq "InstrumentSensitivity" ) { $intotalsens = 1; }
    }

    if ( $intotalsens ) {
      if ( $element->{Name} eq "SensitivityValue" ) { $insensvalue = 1; }
      elsif ( $element->{Name} eq "SensitivityUnits" ) { $insensunits = 1; }
      elsif ( $element->{Name} eq "Frequency" ) { $infrequency = 1; }
    }
  }

  sub end_element {
    my ($self,$element) = @_;

    if ( $element->{Name} eq "Station" ) {
      ($net,$sta) = (undef) x 2;
    }

    elsif ( $element->{Name} eq "Channel" ) {
      ($loc,$chan) = (undef) x 2;
    }

    elsif ( $element->{Name} eq "Epoch" ) {
      # Track epoch count
      $totalepochs++;

      # Translate metadata location ID to "--" if it's spaces
      my $dloc = ( $loc eq "  " ) ? "--" : $loc;

      # Translate commas in metadata instrument name to semi-colons
      $instrument =~ s/,/;/g;

      # Trim sensitivity units to short version, they are returned as, e.g. "M/S - Meters per second"
      ($sensunit) = $sensunit =~ /(.*?)\s\-\s.*/ if ( $sensunit );

      # Cleanup start and end strings, with truncation to 2038-01-01T00:00:00 for older Perls
      my ($y,$mo,$d,$h,$m,$s) = $start =~ /^(\d{4,4}[-\/,:]\d{1,2}[-\/,:]\d{1,2}[-\/,:T]\d{1,2}[-\/,:]\d{1,2}[-\/,:]\d{1,2}).*/;
      my $mstart = ( $y >= 2038 ) ? "2038-01-01T00:00:00" : sprintf ("%04d-%02d-%02dT%02d:%02d:%02d", $y,$mo,$d,$h,$m,$s);
      my ($y,$mo,$d,$h,$m,$s) = $end =~ /^(\d{4,4}[-\/,:]\d{1,2}[-\/,:]\d{1,2}[-\/,:T]\d{1,2}[-\/,:]\d{1,2}[-\/,:]\d{1,2}).*/;
      my $mend = ( $y >= 2038 ) ? "2038-01-01T00:00:00" : sprintf ("%04d-%02d-%02dT%02d:%02d:%02d", $y,$mo,$d,$h,$m,$s);

      # Push channel epoch metadata into storage array
      push (@metadata, "$net,$sta,$dloc,$chan,$start,$end,$lat,$lon,$elev,$depth,$azimuth,$dip,$instrument,$samplerate,$sens,$sensfreq,$sensunit");

      # Put entry into request hash, value is the widest range of channel epochs
      if ( ! exists  $request{"$net|$sta|$dloc|$chan|$rstart|$rend"} ) {
	$request{"$net|$sta|$dloc|$chan|$rstart|$rend"} = "$mstart|$mend";
      }
      else {
	# Track widest metadata start and end range
	my ($vstart,$vend) = split (/\|/, $request{"$net|$sta|$dloc|$chan|$rstart|$rend"});
	my $startepoch = str2time ($mstart);
	my $endepoch = str2time ($mend);
	$vstart = $mstart if ( $startepoch < str2time ($vstart) );
	$vend = $mend if ( $endepoch > str2time ($vend) );
	$request{"$net|$sta|$dloc|$chan|$rstart|$rend"} = "$vstart|$vend";
      }

      # Reset Epoch level fields
      ($start,$end,$lat,$lon,$elev,$depth,$azimuth,$dip,$instrument,$samplerate,$sens,$sensfreq,$sensunit) = (undef) x 13;
      $inepoch = 0;
    }

    if ( $inepoch ) {
      if ( $element->{Name} eq "StartDate" ) { $instart = 0; }
      elsif ( $element->{Name} eq "EndDate" ) { $inend = 0; }
      elsif ( $element->{Name} eq "Lat" ) { $inlat = 0; }
      elsif ( $element->{Name} eq "Lon" ) { $inlon = 0; }
      elsif ( $element->{Name} eq "Elevation" ) { $inelevation = 0; }
      elsif ( $element->{Name} eq "Depth" ) { $indepth = 0; }
      elsif ( $element->{Name} eq "Azimuth" ) { $inazimuth = 0; }
      elsif ( $element->{Name} eq "Dip" ) { $indip = 0; }
      elsif ( $element->{Name} eq "SampleRate" ) { $insamplerate = 0; }

      elsif ( $element->{Name} eq "EquipType" ) { $inequiptype = 0; }

      elsif ( $element->{Name} eq "Response" ) { $intotalsens = 0; }
    }

    if ( $intotalsens ) {
      if ( $element->{Name} eq "SensitivityValue" ) { $insensvalue = 0; }
      elsif ( $element->{Name} eq "SensitivityUnits" ) { $insensunits = 0; }
      elsif ( $element->{Name} eq "Frequency" ) { $infrequency = 0; }
    }
  }

  sub characters {
    my ($self,$element) = @_;

    if ( $element->{Data} ) {
      if ( $instart ) { $start .= $element->{Data}; }
      elsif ( $inend ) { $end .= $element->{Data}; }
      elsif ( $inlat ) { $lat .= $element->{Data}; }
      elsif ( $inlon ) { $lon .= $element->{Data}; }
      elsif ( $inelevation ) { $elev .= $element->{Data}; }
      elsif ( $indepth ) { $depth .= $element->{Data}; }
      elsif ( $inazimuth ) { $azimuth .= $element->{Data}; }
      elsif ( $indip ) { $dip .= $element->{Data}; }
      elsif ( $insamplerate ) { $samplerate .= $element->{Data}; }

      elsif ( $inequiptype ) { $instrument .= $element->{Data}; }

      elsif ( $insensvalue ) { $sens .= $element->{Data}; }
      elsif ( $insensunits ) { $sensunit .= $element->{Data}; }
      elsif ( $infrequency ) { $sensfreq .= $element->{Data}; }
    }
  } # End of SAX MDSHandler
} # End of FetchMetaData()


######################################################################
# MDCallBack:
#
# A call back for LWP downloading of metadata.
#
# Add received data to metadataxml string, tally up the received data
# size and print and updated (overwriting) byte count string.
######################################################################
sub MDCallBack {
  my ($data, $response, $protocol) = @_;
  $metadataxml .= $data;
  $datasize += length($data);

  if ( $verbose ) {
    printf (STDERR "%-10.10s\b\b\b\b\b\b\b\b\b\b", sizestring($datasize));
  }
}


######################################################################
# sizestring (bytes):
#
# Return a clean size string for a given byte count.
######################################################################
sub sizestring { # sizestring (bytes)
  my $bytes = shift;

  if ( $bytes < 1000 ) {
    return sprintf "%d Bytes", $bytes;
  }
  elsif ( ($bytes / 1024) < 1000 ) {
    return sprintf "%.1f KB", $bytes / 1024;
  }
  elsif ( ($bytes / 1024 / 1024) < 1000 ) {
    return sprintf "%.1f MB", $bytes / 1024 / 1024;
  }
  elsif ( ($bytes / 1024 / 1024 / 1024) < 1000 ) {
    return sprintf "%.1f GB", $bytes / 1024 / 1024 / 1024;
  }
  elsif ( ($bytes / 1024 / 1024 / 1024 / 1024) < 1000 ) {
    return sprintf "%.1f TB", $bytes / 1024 / 1024 / 1024 / 1024;
  }
  else {
    return "";
  }
} # End of sizestring()


######################################################################
#
# Package RequestAgent: a superclass for LWP::UserAgent with override
# of LWP::UserAgent methods to set default user agent and handle
# authentication credentials.
#
######################################################################
BEGIN {
  use LWP;
  package RequestAgent;
  our @ISA = qw(LWP::UserAgent);

  sub new
    {
      my $self = LWP::UserAgent::new(@_);
      my $fulluseragent = $useragent;
      $fulluseragent .= " ($appname)" if ( $appname );
      $self->agent($fulluseragent);
      $self;
    }

  sub get_basic_credentials
    {
      my ($self, $realm, $uri) = @_;

      if ( defined $auth ) {
        return split(':', $auth, 2);
      }
      elsif (-t) {
        my $netloc = $uri->host_port;
        print "\n";
        print "Enter username for $realm at $netloc: ";
        my $user = <STDIN>;
        chomp($user);
        return (undef, undef) unless length $user;
        print "Password: ";
        system("stty -echo");
        my $password = <STDIN>;
        system("stty echo");
        print "\n";  # because we disabled echo
        chomp($password);
        return ($user, $password);
      }
      else {
        return (undef, undef)
      }
    }
} # End of LWP::UserAgent override