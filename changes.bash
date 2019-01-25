#!/bin/bash
FILELIST=/home/sysop/filelist
MONITOR_DIR=/home/sysop/output
NEWFILELIST=/home/sysop/newfiles
TEMPFILE=/home/sysop/temp
CURRFILE=/home/sysop/current
[[ -f ${FILELIST} ]] || ls -1 ${MONITOR_DIR} > ${FILELIST}

#while : ; do
cur_files=$(ls -1 ${MONITOR_DIR} | xargs)
echo $cur_files > ${CURRFILE}
#comm -13 ${FILELIST} ${CURRFILE} > ${NEWFILELIST}
diff ${FILELIST} <(echo $cur_files) > ${TEMPFILE}
echo $cur_files > ${FILELIST}
#diff -u -s "$1" "$2" > "/tmp/diff_tmp" 
#add_lines=`cat "/tmp/diff_tmp" | grep ^+ | wc -l`
#added_lines=`cat ${TEMPFILE} | grep ^+ | wc -l`

#echo $added_lines > ${NEWFILELIST}

#    echo "Waiting for changes."
#    sleep $(expr 1 \* 2)
#done
