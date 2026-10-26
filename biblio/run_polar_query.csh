#!/bin/tcsh
#
# Skip over references to GGS Polar and a variety of polar topics (north pole, 
# coronal polar holes, etc.) using search terms and polar_exclude_bibcodes.txt 

run_ads_query_html.py --mission polar \
  --reject_search "Polar vortex,solar polar,aurora,plasma,space weather,bow shock,GGS Polar,geomagnetic,field lines,radiation belt,MHD,stratosphere,corona,corona,magnetosphere,Earth,solar windl" \
  --search "TianGong 2,POLAR" --nocirc
