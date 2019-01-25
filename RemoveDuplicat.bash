#!/bin/bash

catalog=$1

FindTimeWindow.bash $catalog

paste -d" " $catalog TimeWindow.dat > temp.dat

counter2=99
while [ $counter2 -gt 0 ]
do
    gawk '{if(NR==1) {a=$20;b=$21} else {if($20>=a && $20<=b) printf"%d %d\n", NR-1,NR;a=$20;b=$21}}' temp.dat > DuplicateIndex.dat
    gawk '{printf"%d\n%d\n",$1,$2}' DuplicateIndex.dat | sort -n | uniq > DuplicateIndex.dat2
    gawk '{print NR}' temp.dat > AllIndex.dat
    extract AllIndex.dat DuplicateIndex.dat2 > RemainIndex.dat
    gawk '{print "gawk '\''{if(NR=="$1") print $0}'\'' temp.dat"}' RemainIndex.dat | sh >>  temp.temp
    
    input="DuplicateIndex.dat"
    
    cat DuplicateIndex.dat | wc -l
    counter2=`cat DuplicateIndex.dat | wc -l`
    for counter in `gawk '{print NR}' $input`
    do
        index1=`gawk '{if(NR=="'"$counter"'") print $1}' $input`
        index2=`gawk '{if(NR=="'"$counter"'") print $2}' $input`
    
        cc1=`gawk '{if(NR=="'"$index1"'") print $5}' temp.dat`
        cc2=`gawk '{if(NR=="'"$index2"'") print $5}' temp.dat`
    
        high_cc_index=`echo $cc1 $index1 $cc2 $index2 | gawk '{if($1>=$3) print $2;else print $4}'`
    
        echo $high_cc_index >> $input.temp
    
    done
    
    gawk '{print "gawk '\''{if(NR=="$1") print $0}'\'' temp.dat"}' $input.temp | sh > 1.dat
    
    mv 1.dat temp.dat2
    rm $input.temp

    cat temp.dat2 >> temp.temp
    cat temp.temp | sort -n > temp.dat
    rm -rf temp.temp
done

output=`echo $catalog | gawk -F"." '{print $1".Remove"}'`
mv temp.dat $output
