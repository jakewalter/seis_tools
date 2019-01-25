#!/bin/bash

#if [ $# -lt 2 ]
#then 
#  echo "FAIL! Usage: matchcatalogevents.bash /path/catalogPS tempdirectory"
#  exit 0
#fi

#$1="/home/jwalter9/Dropbox/catalogPS"
# create sta.parr and sarr

#for sta in `cut -d\. -f 1 2011*/p.arr | sort -u`; do grep -w $sta 2011*/p.arr | sed 's/p.arr://' | sort -n -k 2 > $sta.parr; done

#for sta in `cut -d\. -f 1 2011*/s.arr | sort -u`; do grep -w $sta 2011*/s.arr | sed 's/s.arr://' | sort -n -k 2 > $sta.sarr; done
#ls -d */201208* > eventslist
ls -d both/* > eventslist

stations=`find both/2012*/*.bp -maxdepth 1 -type f -printf '%f\n' | sort | uniq`
echo -e "$stations\n" > temp.txt


while read line
do
	sta=$line	
	echo "$line blah"
	comp=`echo $sta |cut -d. -f3`
	echo "$comp component"
#	if [[ $comp == BHE ]] || [[ $comp == SHE ]]; then
#  		saclst t2 evlo evla evdp f both/*/$sta | gawk '$2>0' | wfcc -D-2/4/3 | gawk '$7>0.4' | gawk '$7<1.0' | sort -nr -k 7 > $sta.xc
#		echo "yep"
#	elif [[ $comp == BHN ]] || [[ $comp == SHN ]]; then
#		saclst t2 evlo evla evdp f both/*/$sta | gawk '$2>0' | wfcc -D-2/4/3 | gawk '$7>0.4' | gawk '$7<1.0' | sort -nr -k 7 > $sta.xc
#	else
#		saclst t1 evlo evla evdp f both/*/$sta | gawk '$2>0' | wfcc -D-2/4/3 | gawk '$7>0.4' | gawk '$7<1.0' | sort -nr -k 7 > $sta.xc
#		echo "made it to Z comp"
#	fi
	echo "P times"
	temp1=`saclst t1 evlo evla evdp f both/*/$sta | gawk '$2>0' | wc -l`
	echo "$temp1 number of cross corrs"
	saclst t1 evlo evla evdp f both/*/$sta | gawk '$2>0' | wfcc -D-2/4/3 | gawk '$7>0.75' | gawk '$7<1.0' | sort -nr -k 7,7 > $sta.P.xc
	echo "S times"
	temp2=`saclst t2 evlo evla evdp f both/*/$sta | gawk '$2>0' | wc -l`
        echo "$temp2 number of cross corrs"
	saclst t2 evlo evla evdp f both/*/$sta | gawk '$2>0' | wfcc -D-2/4/3 | gawk '$7>0.75' | gawk '$7<1.0' | sort -nr -k 7,7 > $sta.S.xc
	#cc2dt.pl $sta.xc > $sta.dt
done <temp.txt
cat *xc | sort -k 1,1 > temp.xc
cc2dt_v2.pl temp.xc > tempdt.cc     #cc2dt_v2 for hypoDD

#cat *P.xc | sort -k 1,1 > tempP.xc
#cat *S.xc | sort -k 1,1 > tempS.xc
#cc2dt_v3p.pl tempP.xc > tempdt.cc
#cc2dt_v3s.pl tempS.xc >> tempdt.cc


