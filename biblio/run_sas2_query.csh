#!/bin/tcsh
#
# SAS-2 is fairly straightfoward: There are a small number of 
# recent papers that make very passing references to the satellite
# (of the "this source was first seen in 1975 by SAS-2" with no
# further discussion of the SAS-2 observation), so known instances
# of this are screeened out with the sas2_exclude_bibcodes.txt
# file. 

run_ads_query_html.py --mission sas2 \
                      --known sas2_known_bibcodes_20180213.txt
