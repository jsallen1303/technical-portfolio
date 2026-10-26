#!/bin/tcsh
#
# Skips over references to UKIDSS DXS fields

run_ads_query_html.py --mission dxs \
                      --search DXS \
                      --reject_search "UKIDSS" \
                      --known dxs_known_bibcodes_20150406.txt
