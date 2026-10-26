#!/bin/tcsh
#
# A plain search of papers with just "GRANAT" get almost everything... but
# at least one critical paper on the PHEBUS instrument gets missed. So the 
# search below adds the individual instrument names, and thus opens a can of
# worms: there was a PHEBUS on EURECA-1, another is on Bepi-Colombo, there's
# a slew of references to WATCH in various non-Granat contexts, ART-S also 
# brings up ARTS which is used for a variety of non-Granat contexts...
# We apologize for the mess, but it now finds the missing PHEBUS and other
# papers!

#run_ads_query_html.py --mission granat \
#                      --known granat_known_bibcodes_19990505.txt

run_ads_query_html.py --mission granat \
                      --search "Granat,PHEBUS,WATCH,ART-P,ART-S,KONUS-B" \
                      --reject_search "MESSENGER,Bepi-Colombo,Mercury,ultraviolet spectroscopy,Atmospheric Radiative,Automated Rock Thin,AGN Watch,Web Watch,Apertif Radio Transient System,radiative transfer model,AMSR2,AMSR-E,microwave,EURECA" \
                      --reject_journal "PhyEd" \
                      --known granat_known_bibcodes_19990505.txt
