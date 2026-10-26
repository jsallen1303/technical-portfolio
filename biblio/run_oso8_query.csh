#!/bin/tcsh
#
# OSO-8 is a solar mission with several instruments, many of them 
# solar (surprise!) instruments unrelated to high energy astrophysics
# Therefore, there is bit of filtering of the results to reject the 
# purely solar-related publications. Even with the reject filter setting,
# some solar papers are found and thus listed in oso8_exclude_bibcodes.txt

run_ads_query_html.py --mission oso8 \
                      --reject_search "solar,Sun,sunspot,SOHO,Lyman" \
                      --known oso8_known_bibcodes_20150326.txt
