#!/bin/bash
rm -rf HRSN*
each=$1

gawk '{print $0}' 9times_$each.dat > HRSN_stack_detection_mag_MAD_9.dat

#gawk '{print "gawk '\''{if($4=="$7") print $0}'\'' 15times_'$each'"}' SC_2008_2010_sjf_5km_12more.catalog | sh > HRSN_stack_detection_mag_MAD_9.dat
make HRSN_stack_detection_mag_MAD_9_ms.dat
matlab -nodisplay -nojvm -nodesktop -nosplash < best_detection.m
make HRSN_stack_detection_mag_MAD_9_final_uniq.dat
./gen_best_detection_loop.bash
./gen_best_detection_loop.bash
./gen_best_detection_loop.bash
./gen_best_detection_loop.bash
./gen_best_detection_loop.bash
./gen_best_detection_loop.bash
./gen_best_detection_loop.bash
./gen_best_detection_loop.bash
./gen_best_detection_loop.bash
./gen_best_detection_loop.bash
./gen_best_detection_loop.bash
./gen_best_detection_loop.bash
./gen_best_detection_loop.bash
gawk '{print $0,"'"$each"'"}' HRSN_stack_detection_mag_MAD_9_final_uniq_clean.dat > 9times_$each.new
cp 9times_$each.new HRSN_stack_detection_mag_MAD_9_final_uniq_clean.dat2
make HRSN_stack_detection_mag_MAD_9_final_uniq_amp_ratio
paste -d" " HRSN_stack_detection_mag_MAD_9_final_uniq_clean.dat2 HRSN_stack_detection_mag_MAD_9_final_uniq_amp_ratio.dat > HRSN_stack_detection_mag_MAD_9_final_uniq_clean_amp_ratio.dat
#expand_catalog.bash $each HRSN_stack_detection_mag_MAD_9_final_uniq_clean_amp_ratio.dat

#RemoveDuplicat.bash 15times_$each.catalog
