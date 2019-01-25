#!/bin/bash

basedir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
seiscomp_root=/home/seiscomp/seiscomp3
d=`date -u +%Y-%m-%dT%H:%M:%S.%6NZ`
epoch=`date -u --date=$d +%s.%6N`

scxmldump -d mysql://sysop:sysop@localhost/seiscomp3 -E $1 -PMAfp |  xsltproc $SEISCOMP_ROOT/share/xml/0.10/sc3ml_0.10__quakeml_1.2.xsl - | xsltproc --stringparam current-date $d --stringparam epoch $epoch /home/sysop/bin/xsl/anss.xsl - > /home/sysop/output/$1_update.xml
scp /home/sysop/output/$1_update.xml analyst@keokuk.ogs.ou.edu:/home/analyst/etc/quakeml/
