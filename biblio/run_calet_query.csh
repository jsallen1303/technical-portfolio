#!/bin/tcsh

run_ads_query_html.py --mission calet \
                      --search "CALET,Calorimetric Electron Telescope" \
                      --reject_search "bCALET" --nocirc
