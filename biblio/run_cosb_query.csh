#!/bin/tcsh
#
# There is an instrument on HST called COS (Cosmic Origins Spectrograph)
# installed in May 2009, so a lot of papers since then come up positive
# for COS-B with HST results. There are also a number of papers which 
# mention cos functions (often "cos b/theta" kinds of things) that 
# still generate false matches that need manual filtering

run_ads_query_html.py --mission cosb \
                      --search "COS B,COS-B" \
                      --reject_search "HST,Hubble Space Telescope" \
                      --known cosb_known_bibcodes_20180213.txt
 
