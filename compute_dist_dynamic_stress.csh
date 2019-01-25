#!/bin/csh

# simple shell script to compute the dynamic stress for eqs listed in the ANSS
# catalog using the surface wave magnitude formula listed in the vanderElst and Brodsky (2010)
# JGR paper (http://onlinelibrary.wiley.com/doi/10.1029/2009JB006681/abstract)
# First we obtain displacement (in cm), then we get velocity in (cm/s) assuming a 20-s surface wave.
# Finallly we convert velocity to dynamic stress in MPa by dividing 10 (assuming 3.5 km/s
# wave speed and 35 GPa shear modulus), or times 100 to get KPa
# rule of thumb, 1 cm/s corresponds to 0.1 MPa, or 100 KPa.
# Last updated by zpeng, Wed Aug 20 11:11:41 EDT 2014

if ($#argv == 3 ) then
	set stnm = $1
	set stlo = $2
	set stla = $3
else 
	set stnm = "TPUB"
	set stlo = 120.6296
	set stla = 23.3005
# set up a default parameter, say station TW.TPUB
endif

# change to the local directory where you download the catalog
set ANSS_cat = ANSS_depth_100_mag_75_yr_1998_reformat.dat

set temp_dist = `printf "$stnm\n" | awk '{print $1".dist.tmp"}'`
set output  = `printf "$stnm\n" | awk '{print $1"_ANSS_disp_ds.dat"}'`

set dist2deg = "111.19"

awk '{print $7,$8}' $ANSS_cat | ndistbaz $stlo $stla | awk '{printf "%.3f\n",$1/"'"$dist2deg"'"}' > $temp_dist

# default, only check the shallow eq. (less than 100 km) and magnitude larger than 5.5
# and distance larger than 500 km
# for distance shorter than 500 km, we use the unconstrained best fitting parameters
# to estimate the PGV in cm/s, and then output the dynamic stress by timing 100
paste -d" " $temp_dist $ANSS_cat | awk '{if ($10<=100 && $11>=5.5 && $1*111.19>=800) printf "%11.7f %8.4f %4s %2s %2s %2s %2s %5.2f %9.4f %8.4f %7.2f %4.2f\n",10^($11-1.66*log($1)/log(10)-6)*2*3.14159/20*100,$1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11; else if ($10<=100 && $11>=5.5 && $1*111.19<800) printf "%11.7f %8.4f %4s %2s %2s %2s %2s %5.2f %9.4f %8.4f %7.2f %4.2f\n",10^(-2.29+0.85*$11-1.29*log($1*111.19)/log(10))*100,$1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11}' | sort -n -r > $output

rm -rf $temp_dist

printf "Finish computing the distance and dynamic stress for station $stnm\n"
