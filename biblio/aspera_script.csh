#!/bin/tcsh

# Run search excluding mention of ASPERA 3 (instrument at Mars) and ASPERA 4 (instrument
# at Venus). Some known references unrelated to these terms nor the Aspera mention are
# excluded by aspera_exclude_bibcodes

python ./run_ads_query_html.py --mission "aspera" -rs "ASPERA 3, ASPERA 4, Venus, Mars"
