#!/bin/tcsh
# I do not know why ADS results searching under "collection:astronomy"
# return Earth Science results (and some times, fail to find astronomy
# results), but exclusions here are included to reject certain Earth 
# Science and terms with ANS. Bibcodes with false positives on "ans"
# from German and French language references also occasionally show up 
# and require checking manually and adding to ans_exclude_bibcodes.txt
# as found

run_ads_query_html.py --mission ans \
                      --search "ANS" \
                      --reject_search "ANS Collaboration,Asiago Novae and Symbiotic,Arabian-Nubian Shield,Arabian Shield,Afanasy Nikitin seamount,neutron spectrometer,autonomic nervous system,air navigation systems" \
                      --known ans_known_bibcodes_19990811.txt
