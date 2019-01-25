#!/bin/bash
for f in *xml; do java -jar ~/bin/stationxml-converter-1.0.9.jar --seed "$f" -o "$f".dataless; done
