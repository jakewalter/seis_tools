#!/usr/bin/env python
from __future__ import division
from __future__ import print_function
from obspy.clients.fdsn.mass_downloader import RectangularDomain, CircularDomain, Restrictions, MassDownloader
from obspy import UTCDateTime
from obspy.clients.fdsn import Client

starttime = UTCDateTime("2016-01-01T00:00:00.000")
#2000
endtime = UTCDateTime("2018-01-01T00:00:00.000")

#client = Client("IRIS")
#domain = CircularDomain(36.429,-96.923,minradius=0.0, maxradius=2.0)
#domain = RectangularDomain(minlatitude=33.5, maxlatitude=38,minlongitude=-101, maxlongitude=-94)
#restrictions = Restrictions(starttime=starttime, endtime=endtime,reject_channels_with_gaps=True,minimum_length=0.75,minimum_interstation_distance_in_m=10E3, channel_priorities=["HH[NE12Z]", "BH[NE12Z]", "SH[NEZ]"],location_priorities=["", "00", "10"])

domain = CircularDomain(35.7,-98,minradius=0.0, maxradius=4.0)

restrictions = Restrictions(starttime=starttime, endtime=endtime,chunklength_in_sec=86400,reject_channels_with_gaps=False,minimum_length=0,minimum_interstation_distance_in_m=100, channel_priorities=["HH[NE12Z]","BH[NE12Z]","EH[NE12Z]","SH[NE12Z]"],location_priorities=["", "00", "10"])

mdl = MassDownloader(providers=["IRIS"])
mdl.download(domain, restrictions, threads_per_client=3, mseed_storage="/data/okla/waveforms",stationxml_storage="/data/okla/stations")
