#!/bin/bash

ls -d 12times_2012???? > outputlist

cat $thislist | while read line1
do
listnow=`echo $line1`
echo $listnow
done
