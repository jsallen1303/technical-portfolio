#!/bin/tcsh
#
# MAXI appears in many GCN circulars, which are excluded here
# References to the iSEEP Wide Field MAXI (NOT the same as MAXI though planned
# to be attached to JEMS on the ISS, so it is confusing...) are also excluded
#
# maxi_exclude_bibcodes.txt also contains some irregular items that show up in 
# an ADS search, but are unrelated to the MAXI instrument on the ISS

run_ads_query_html.py --mission maxi \
                      --search "MAXI,Monitor of All-Sky Image" \
                       --reject_search "WF-MAXI,iWF-MAXI" --nocirc
