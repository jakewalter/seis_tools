#!/bin/bash
if [ $# -lt 2 ]
then 
  echo "FAIL! Usage: matchcatalogevents.bash /path/catalogPS tempdirectory"
  exit 0
fi

#$1="/home/jwalter9/Dropbox/catalogPS"

cat $1 | while read line1
do
listnow=`echo $line1`

echo $listnow | while read line
do
eventname=`echo $line | gawk '{print $1}'`

#echo "$eventname"
if [ -d "$eventname" ]; then
	echo "$eventname"
	cp -r $eventname $2
fi
done
done
