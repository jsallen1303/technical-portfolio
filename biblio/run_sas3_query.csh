#!/bin/tcsh
#
# SAS-3 is fairly straightfoward: there is a spurious match to 
# the MWC SAS3 instrument on the microsatellite Chibis-M and 
# the sas3_exclude_bibcodes list of known false references only
# needs filter out a photometry paper that makes a very glancing
# reference to SAS-3

run_ads_query_html.py --mission sas3 \
                      --reject_search "MWC,Chibis" \
                      --known sas3_known_bibcodes_20150326.txt
