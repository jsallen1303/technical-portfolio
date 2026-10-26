#!/bin/tcsh
#
# Filter out GCN references

/usr1/local/anaconda_py3/bin/python run_ads_query_html.py --mission "grbbeta" --reject_journal "GCN"
