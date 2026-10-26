#!/bin/tcsh

# Yes, this is crazy, but there are so many ways to generate false positives OR 
# miss references for XQC (and this STILL manages to miss a very small few: the 
# user may need to occasionally try a manual search for "sounding rocket" AND 
# "calorimeter" without limiting to "collection:astronomy" and see if something new
# and relevant shows up)

#run_ads_query_html.py --mission xqc \
#                      --search "XQC,X-Ray Quantum Calorimeter,X-ray microcalorimeter" \
#                      --reject_search "Lynx,TES,transition-edge sensor,transition edge,Astro-H,Astro-E,Astro-E2,SQUID,SXS,XRS,Hitomi,XRISM,ATHENA,EBIT,MKIDs,IXO,ATHENA,Spectr-RG,SRG,SXC,germanium,Constellation,DXS,NeXT,XMM,Newton,Suzaku,IMBOSS"

# Instead of the long search and reject of above, made a hard-coded version which performs
# an addition search on papers with McCammon, D and diffuse X-ray studies to find more XQC
# (and accidentally, WSSC) results missed otherwise

run_ads_query_xqc_html.py --known xqc_known_bibcodes_20200617a.txt
