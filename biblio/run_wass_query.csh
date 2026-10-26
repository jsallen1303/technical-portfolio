#!/bin/tcsh

# Yes, this is crazy, but there are so many ways to generate false positives OR 
# miss references for WASS (and there's oodles more that have to be rejected
# "manually" with wass_exclude_bibcodes.txt: lots of groups were sending up sounding
# rockets with various kinds of X-ray detectors in the 1970s).. Some "known" references
# were also found by running the XQC search, and finding references that predate XQC
# but clearly were related to the Wisconsin rocket project

run_ads_query_html.py --mission wass \
                      --search "diffuse X-ray background,Wisconsin Sky Survey,X-ray sounding rocket" \
                      --reject_search "Lynx,TES,transition-edge sensor,transition edge,Astro-H,Astro-E,Astro-E2,SQUID,SXS,XRS,Hitomi,XRISM,ATHENA,EBIT,MKIDs,IXO,ATHENA,Spectr-RG,SRG,SXC,germanium,Constellation,DXS,NeXT,XMM,Newton,Suzaku,IMBOSS,ROSAT" \
                      --year "1970-1995" \
                      --known wass_known_bibcodes_20200612.txt
