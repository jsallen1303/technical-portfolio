#!/bin/tcsh
#
# Mikhail Lomonosov was a polymath who investigated (and made major advances)
# in a wide variety of science topics. As a result, his name appears in a 
# large number of references related to various topics other than the 
# MKL-300 astronomy satellite. The following search terms (and the 
# lomonosov_exclude_bibcodes.txt file) should eliminate most unrelated to 
# the satellite, though it still includes some intruments on MKL-300 that were
# not related to high energy astrophysics.
# There may be some missing references where authors were from MGU (Moscow
# State University) writing about the satellite

run_ads_query_html.py --mission lomonosov \
    --reject_search "Moscow State University,Lomonosov Crater,Lomonosov Ridge,Venus,Lomonosov Rise,Lomonosov-Fleming" \
    --nocirc

