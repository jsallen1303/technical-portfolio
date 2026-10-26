#!/bin/tcsh
#
# The excluded bibcodes are papers about subjects unrelated to hakucho,
# but make a very empty passing mention that the mission happened.

run_ads_query_html.py --mission hakucho \
                      --search "Hakucho,CORSA-b" \
                      --known hakucho_known_bibcodes_19990810.txt

