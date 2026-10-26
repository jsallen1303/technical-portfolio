#!/bin/tcsh
#
# Skip over references to Athena (II) rockets, ATHENA magnetohydrodyamic code,
# archaeology related to a certain goddess, the ATHENA mars rover, etc.

run_ads_query_html.py --mission athena \
                      --reject_search "rocket motor,Mars,rover,code,MHD,hydrodynamics,laser"
