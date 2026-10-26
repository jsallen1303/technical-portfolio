#!/bin/tcsh
#
# Need earlier python version for this code
# Filter out GCN references

/usr1/local/anaconda_py3/bin/python run_ads_query_html.py --mission "glowbug" --reject_journal "GCN"
