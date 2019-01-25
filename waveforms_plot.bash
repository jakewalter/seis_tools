#!/bin/bash

counter=$1

cc=`gawk '{if(NR=='"$counter"') print $5}' ../All.catalog.March.2013`
mad=`gawk '{if(NR=='"$counter"') print $7}' ../All.catalog.March.2013`
mag=`gawk '{if(NR=='"$counter"') print $3}' ../All.catalog.March.2013`

num=`ls *.z | wc -l`
num2=`echo $num | gawk '{print $1+1}'`

saclst t1 f *.z | gawk '{print $2,$1}' | sort -n -r | gawk '{print $2" 0",NR,"1p/128/128/128"}' |  pssac -JX2/8 -R-5/10/0/$num2 -K -P -W1 -M0.5 -Ent-3 -Y2 -Ba5f1:"Time (s)":S -r -C-5/10 > waveform.ps

ls *.z | gawk -F"." '{printf"-5 %f 14 0 0 ML %s\n",NR+0.5,$1}' | pstext -JX -R -K -P -O -N -G0/0/0 >> waveform.ps

saclst t1 f *.z | gawk '{print $2,$1}' | sort -n -r | gawk '{printf"%f %f\n%f %f\n",$1,NR-0.5,$1,NR+0.5}' | psxy -JX -R -K -P -O -W1p/255/0/0 >> waveform.ps
saclst t2 f *.z | gawk '{print $2,$1}' | sort -n -r | gawk '{printf"%f %f\n%f %f\n",$1,NR-0.5,$1,NR+0.5}' | psxy -JX -R -K -P -O -W1p/2/0/255 >> waveform.ps


num=`ls *.r | wc -l`
num2=`echo $num | gawk '{print $1+1}'`

saclst t1 f *.r | gawk '{print $2,$1}' | sort -n -r | gawk '{print $2" 0",NR,"1p/128/128/128"}' |  pssac -JX2/8 -R-5/10/0/$num2 -K -P -O -W1 -M0.5 -Ent-3 -X2.1 -Ba5f1:"Time (s)":S -r -C-5/10 >> waveform.ps

ls *.r | gawk -F"." '{printf"-5 %f 14 0 0 ML %s\n",NR+0.5,$1}' | pstext -JX -R -K -P -O -N -G0/0/0 >> waveform.ps

saclst t1 f *.r | gawk '{print $2,$1}' | sort -n -r | gawk '{printf"%f %f\n%f %f\n",$1,NR-0.5,$1,NR+0.5}' | psxy -JX -R -K -P -O -W1p/255/0/0 >> waveform.ps
saclst t2 f *.r | gawk '{print $2,$1}' | sort -n -r | gawk '{printf"%f %f\n%f %f\n",$1,NR-0.5,$1,NR+0.5}' | psxy -JX -R -K -P -O -W1p/2/0/255 >> waveform.ps


num=`ls *.t | wc -l`
num2=`echo $num | gawk '{print $1+1}'`

saclst t1 f *.t | gawk '{print $2,$1}' | sort -n -r | gawk '{print $2" 0",NR,"1p/128/128/128"}' |  pssac -JX2/8 -R-5/10/0/$num2 -K -P -O -W1 -M0.5 -Ent-3 -X2.1 -Ba5f1:"Time (s)":S -r -C-5/10 >> waveform.ps

ls *.r | gawk -F"." '{printf"-5 %f 14 0 0 ML %s\n",NR+0.5,$1}' | pstext -JX -R -K -P -O -N -G0/0/0 >> waveform.ps

saclst t1 f *.t | gawk '{print $2,$1}' | sort -n -r | gawk '{printf"%f %f\n%f %f\n",$1,NR-0.5,$1,NR+0.5}' | psxy -JX -R -K -P -O -W1p/255/0/0 >> waveform.ps
saclst t2 f *.t | gawk '{print $2,$1}' | sort -n -r | gawk '{printf"%f %f\n%f %f\n",$1,NR-0.5,$1,NR+0.5}' | psxy -JX -R -K -P -O -W1p/2/0/255 >> waveform.ps

id=`pwd | gawk -F"/" '{print $NF}'`
echo -5 -0.5 16 0 0 MR $id $cc $mad $mag | pstext -JX -R -P -O -N -G0/0/0 >> waveform.ps
