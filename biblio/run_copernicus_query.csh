#!/bin/tcsh
#
# Search for OAO (though this gets OAO-2 and OAO B as well as OAO-C/-3), 
# and try to reject references to the Suburu Telescope (which has a OAO
# instrument (?)), the Okayama Astronomical Observatory, the Odessa 
# Astronomical Observatory, the MITSuME instrument at Okayama, a slew of 
# papers in the 2010s about OAO 1657-415 (none of which refer to the original
# Copericus observation). There is still a great deal of noise in the 
# results (since OAO-3 had a UV instrument), so there is still a large 
# collection of undesired references collected in the cop_exclude_bibcodes.txt
# file

run_ads_query_html.py --mission cop \
                      --search "OAO,UCLXE" \
                      --reject_search "Ultraviolet,1657-415,Subaru,MITSuME,Okayama" \
                      --known cop_known_bibcodes_20180213.txt
