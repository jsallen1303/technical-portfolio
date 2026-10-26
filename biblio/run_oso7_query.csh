#!/bin/tcsh
#
# OSO-7 is a solar mission with several instruments, many of them 
# solar (surprise!) instruments unrelated to high energy astrophysics
# Therefore, there is bit of filtering of the results to reject the 
# purely solar-related publications. Even with the reject filter setting,
# some solar papers are found and thus listed in oso7_exclude_bibcodes.txt

run_ads_query_html.py --mission oso7 \
                      --reject_search "chromosphere,Sun,sunspot,SOHO,Lyman" \
                      --known oso7_known_bibcodes_20160707.txt
