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
ls -d 20* > eventslist 

stations=`find */*.bp -maxdepth 1 -type f -printf '%f\n' | sort | uniq`
echo -e "$stations\n" > temp.txt

while read line
do
	sta=$line	
	echo "$line blah"
	saclst t2 evlo evla evdp f */$sta | wfcc -D-2/4/3 | gawk '$7>0.5' | gawk '$7<1.0' | sort -nr -k 7 > $sta.xc
	cc2dt.pl $sta.xc > $sta.dt
done <temp.txt


