#!/bin/tcsh

run_ads_query_html.py --mission vela5b \
                      --search "Vela 5B,XC" \
                      --reject_search "ART-XC,X(C)" \
                      --known vela5b_known_bibcodes_20180214.txt
