#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 13:47:18 2019
Version 0.0
First cut at Python 3 code to quary ADS for 'CALET' in title or abstract
Performs TWO searches (one on title, other on abstract) to get all instances
where EITHER CALET appears in title OR abstract text.
Writes all bibcodes found, all unique bibcodes, citations with
author and title, and a simple HTML table with all references for
ease of exploration

Version 0.1
Added search through the body of the text: this will generate MANY
more results, most of which will not references to the CALET mission
but does garnish some addition genuine results buried in a lot of noise

Version 0.2 (26 May 2020)
Get arguments from the command line to support:
    * user specified missions (not just CALET anymore)
    * user specified date range
    * user specified file of known references to skip
    * user specified file of known irrelevant references to skip
    * HTML list output (replacing earlier version table format)
      for starting/appending to bibliographies in HEASARC pages
    * user specified search term which may be different from mission name
      E.g. --mission 'XQC' --search 'X-ray Quantum Calorimeter'

Version 0.3 (29 May 2020)
Added --nogcn option to skip over GCN references (code extendable to other volumes to reject)

Version 0.4 (1 Jun 2020)
Added --reject_volumne (e.g. --reject_volume 'GRL') to reject undesired journals,
 though --nocirc is probably more useful (rejects GCN, IAUC, ATel)
Added --reject_search for terms to reject (e.g. --search 'X-ray Calorimeter' --reject_search 'Lynx','Hitomi')
Extended --search to allow simultaneous multiple search terms (e.g. --search "XQC,X-ray Quantum Calorimeter,X-ray Microcalorimeter")
Replaced --nogcn with --nocirc to filter out more telegrams, circulars, etc. than just GCN (GRB Coordinates Network)
Added 'pub' to ADS request to get full name of conferences, reports, books, and non-journal type references

Version 0.5 (5 Jun 2020)
Convert (many) special characters into HTML entities in HTML output 

Version 0.6 (8 Jun 2020)
Add --full option to do a search through the entire paper for search terms, not just 
abstract and title

Version 0.7 (10 Jun 2020)
Add --seed_refereed and --seed_nonrefereed options to allow known bibcodes 
to be read in to generate a complete list of references that include these 
known references in the HTML output
(default NONE)
Uses --abs search instead of --title and --abstract (includes title, abstract, and keywords)
Uses normalized author list (E.g. Angelini, L rather than Angelini, Lorella) in HTML output

Version 0.8 (14 Jun 2020)
Remove --seed_refereed and --seed_nonrefereed options (i.e. do not require 
user to sort known references into refereed and non-refereed sources: this 
code will now do that for them). Change --known to get known references 
brought in and included.

Version 0.81 (15 Jun 2020)
Added datetime to stamp datestring on output files
Added a new (missionname)_known_bibcodes_(date).txt output file

Version 0.82
Sort complete list of bibcodes in same order as references (reverse chronological, alphabetically within years)

Version 0.83 (6 Sep 2020)
Add --nosearch option to permit HTML creation from a list of known bibcodes
 with no further updates from ADS
Add HEASARC standard HTML bibliography page creation 
Add --template optio to create an HTML main bibliography page template 

TO DO

add --verbose function


@author: Jesse Allen (NASA/GSFC HEASARC)
"""

from urllib.parse import quote
from datetime import date
import sys
import argparse
import requests

def include_result(value, reject):
    accept = True
    for test in reject:
        if value == test:
            accept = False
    return accept


def bibcode_decode(bibcode):
    year = bibcode[:4]
    qualifier = bibcode[13].replace('.', '')
    page = bibcode[14:18].replace('.', '')
    # Occasionally (usually GCN), "volume" has too many digits and leaks into journal
    # and page is meaningless in a circular (i.e. always 1)
    if bibcode[8].isdigit():
        journal = bibcode[4:8].replace('.', '')
        volume = bibcode[8:13]
        if page == '1':
            page = ''
    else:
        journal = bibcode[4:9].replace('.', '')
        volume = bibcode[9:13].replace('.', '')

     # In case of five-digit page number, the first digit is in the ADS qualifier column
    if qualifier.isdigit():
        page = "%s%s" % (qualifier, page)
        qualifier = ''
    else:
        # L qualifier for Letters (changes journal abbrevation (ApJ only?) and page)
        # P for pink page
        # E for electronic abstract
        #standard_qualifiers = ['L','E','P']
        standard_qualifiers = ['L', 'P']
        for letter in standard_qualifiers:
            if letter in qualifier:
                page = "%s%s" % (letter, page)
                if 'ApJ' in journal and 'L' in letter:
                    journal = 'ApJL'
        # Physical Review and others has pages above 9999, or Issues, and
	# indicates this with an alphabetically ordered: e.g. "c1008" means
	# "031008" (Issue 3, pg 1008)
        if qualifier.islower():
            lead_digit = ord(qualifier) - 96
            page = "%02d%s" % (lead_digit, page)
    return year, journal, volume, qualifier, page


def bib_query(search_terms, reject_bib, reject_journal):
    ads_token = 'Z2wFKcJJoGtRAyDSoRX9kXa2j9Q6CvNUftg3jvFd'
    query_rows = 10000
    query_url = 'https://api.adsabs.harvard.edu/v1/search/query'
    query_params = {
        'q': search_terms,
        'wt': 'json',
        'rows' : query_rows,
        'fl': 'bibcode,title,author,citation_count,pub,author_norm'
    }
    query_headers = {'Authorization' : 'Bearer %s' % ads_token}
    query_response = requests.get(
        query_url,
        params=query_params,
        headers=query_headers
    )
#    count = query_response.json()['response']['numFound']
#    print("Query returns %d references" % (count))
    all_ads_results = query_response.json()['response']['docs']
    bibbase_url = 'https://ui.adsabs.harvard.edu/abs/'
    filtered_ads_results = []
    for paper in all_ads_results:
        bibcode = paper['bibcode']
        year, journal, volume, qualifier, page = bibcode_decode(bibcode)
        if include_result(paper['bibcode'], reject_bib) and include_result(journal, reject_journal):
            encoded_bibcode = quote(bibcode)
            abstract_url = bibbase_url + encoded_bibcode + '/abstract'
            # Some papers lack an author
            if not 'author' in paper:
                paper['author'] = None
                paper['author_norm'] = None
            if not 'citation_count' in paper:
                paper['citation_count'] = 0
            if not 'title' in paper:
                paper['title'] = 'Untitled'
            bib_list = {
                'author': paper['author'],
                'author_norm': paper['author_norm'],
                'year': year,
                'bibcode': bibcode,
                'abstract_url': abstract_url,
                'title': paper['title'][0],
                'citation_count': paper['citation_count'],
                'publication': paper['pub']
            }

            filtered_ads_results.append(bib_list)
    return filtered_ads_results

# A far-from-comprehensive list of common Unicode characters and HTML entities to match them
def unicode_to_html_entity(line):
    substitute = {
        '—': '&mdash;',
        '–': '&ndash;',
        '&': '&amp;',
        '≤': '&le;',
        '≥': '&ge;',
        '~': '&sim;',
        '≈': '&thickapprox;',
        '˚': '&deg;',
        '±': '&plusmn;',
        '∓': '&mnplus;',
        '≡': '&equiv;',
        'Ä': '&Auml;',
        'ä': '&auml;',
        'Ë': '&Euml;',
        'ë': '&euml;',
        'Ï': '&Iuml;',
        'ï': '&iuml;',
        'Ö': '&Ouml;',
        'ö': '&ouml;',
        'Ü': '&Uuml;',
        'ü': '&uuml;',
        'Å': '&Aring;',
        'å': '&aring;',
        'À': '&Agrave;',
        'à': '&agrave;',
        'È': '&Egrave;',
        'è': '&egrave;',
        'Ì': '&Igrave;',
        'ì': '&igrave;',
        'Ò': '&Ograve;',
        'ò': '&ograve;',
        'Ù': '&Ugrave;',
        'ù': '&ugrave;',
        'Â': '&Acirc;',
        'â': '&acirc;',
        'Ê': '&Ecirc;',
        'ê': '&ecirc;',
        'Î': '&Icirc;',
        'î': '&icirc;',
        'Ô': '&Ocirc;',
        'ô': '&ocirc;',
        'Û': '&Ucirc;',
        'û': '&ucirc;',
        'Á': '&Aacute;',
        'á': '&aacute;',
        'É': '&Eacute;',
        'é': '&eacute;',
        'Í': '&Iacute;',
        'í': '&iacute;',
        'ń': '&nacute;',
        'Ó': '&Oacute;',
        'ó': '&oacute;',
        'ś': '&sacute;',
        'Ú': '&Uacute;',
        'ú': '&uacute;',
        'Ç': '&Ccedil;',
        'ç': '&ccedil;',
        'Ã': '&Atilde;',
        'ã': '&atidle;',
        'Ñ': '&Ntilde;',
        'ñ': '&ntilde;',
        'Õ': '&Otidle;',
        'õ': '&otidle;',
        'ł': '&lstrok;',
        'ß': '&szlig;',
        'Ð': '&ETH;',
        'ð': '&eth;',
        'Ø': '&Oslash;',
        'ø': '&oslash;',
        'Æ': '&AElig;',
        'æ': '&aelig;',
        'Þ': '&THORN;',
        'þ': '&thorn;',
        'α': '&alpha;',
        'β': '&beta;',
        'χ': '&chi;',
        'Δ': '&Delta;',
        'δ': '&delta;',
        'ε': '&epsilon;',
        'η': '&eta;',
        'Γ': '&Gamma;',
        'γ': '&gamma;',
        'ι': '&iota;',
        'κ': '&kappa;',
        'Λ': '&Lambda;',
        'λ': '&lambda;',
        'μ': '&mu;',
        'ν': '&nu;',
        'Ω': '&Omega;',
        'ω': '&omega;',
        'Ο': '&Omicron;',
        'ο': '&omicron;',
        'Φ': '&Phi;',
        'φ': '&phi;',
        'Π': '&Pi;',
        'π': '&pi;',
        'Ψ': '&Psi;',
        'ψ': '&psi;',
        'ρ': '&rho;',
        'Σ': '&Sigma;',
        'σ': '&sigma;',
        'τ': '&tau;',
        'θ': '&theta;',
        'υ': '&upsilon;',
        'ζ': '&zeta;'
        }
    new_line = line
    for character in substitute:
        new_line = new_line.replace(character, substitute[character])
    # In case there was HTML already there...
    new_line = new_line.replace('&amp;amp;', '&amp;') 
    new_line = new_line.replace('&amp;gt;', '&gt;') 
    new_line = new_line.replace('&amp;ge;', '&ge;') 
    new_line = new_line.replace('&amp;lt;', '&lt;')
    new_line = new_line.replace('&amp;le;', '&le;')
    new_line = new_line.replace('&amp;mdash;', '&mdash;')
    return new_line

def bibcode_to_htmllist(catalog):
    html_list = ''
    for item in catalog:
        link_line = '<li><b><a href=\"' + item['abstract_url'] + '\"\n'
        link_line += '          style=\"color:#0000ff\">\n'
        html_title = unicode_to_html_entity(item['title'])
        title_line = '    ' + html_title + '</a></b><br>\n'
        if item['author_norm'] is None:
            author_line = ''
        else:
            author_list = []
            for author in item['author_norm']:
                author_list.append(unicode_to_html_entity(author))
            if len(author_list) == 1:
                author_line = author_list[0] + ', '
            elif len(author_list) == 2:
                author_line = author_list[0] + ' &amp; ' + author_list[1] + ', '
            elif len(author_list) == 3:
                author_line = author_list[0] + ', ' + author_list[1] + ' &amp; ' + author_list[2] + ', '
            else:
                author_line = author_list[0] + ' <i>et al.</i>, '
        year, journal, volume, qualifier, page = bibcode_decode(item['bibcode'])
        # Deal with cases of conferences, proceedings books, colloquia, workshops,
        # reports, and proposals
        conf_flag = False
        standard_conferences =[ 'conf', 'proc', 'book', 'coll', 'work', 'rept', 'prop']
        for conf in standard_conferences:
            if conf in volume:
                conf_flag = True
        # Some conferences look like journals still: here's a non-comprehensive list
        other_conferences = ['APS', 'ICRC', 'cosp', 'AIPC', 'LPICo']
        for conf in other_conferences:
            if conf == journal:
                conf_flag = True
        html_journal = unicode_to_html_entity(journal)
        # Handle instances of PhD Thesis citations
        if 'PhDT' in journal:
            ref_line = "    %sPhD Thesis, %s (%s)</li>\n" % (
                author_line,
                page,
                year
                )
        # Handle circulars and notices with no page numbers
        elif page == '':
            ref_line = "    %s%s %s (%s)</li>\n" % (
                author_line,
                html_journal,
                volume,
                year
                )
        else:
            # Use full name of conference, report, proceedings, book, colloquia, workshop, or report
            if conf_flag:
                conference_name = item['publication'].replace('&', '&amp;')
                ref_line = "    %s%s, %s (%s)</li>\n" % (
                    author_line,
                    conference_name,
                    page,
                    year
                    )
            else:
                ref_line = "    %s%s, <b>%s</b>, %s (%s)</li>\n" % (
                    author_line,
                    html_journal,
                    volume,
                    page,
                    year
                    )
        html_list = html_list + link_line + title_line + ref_line
    return html_list

# Given a mission name with a number, split on number 
# (e.g. "venera14" becomes ['venera','14']). This ALMOST 
# always gets the results desired
def text_num_split(item):
    for index, letter in enumerate(item, 0):
        if letter.isdigit():
            return [item[:index],item[index:]]


# Main program
VERSION = '0.83'
circulars = ['GCN', 'AAVSC', 'BAAVC', 'IAUC', 'JASAC', 'NASCL', 'ATel']
# Start by parsing command line arguments, if any
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--version", help="show program version",
                    action="store_true")
parser.add_argument("-m", "--mission",
                    help="search ADS for abstracts with mission cited in abstract or title")
parser.add_argument("-s", "--search",
                    help="search ADS for abstracts with search term in title and/or abstract")
parser.add_argument("-rs", "--reject_search",
                    help="ignore results with search term")
parser.add_argument("-rj", "--reject_journal",
                    help="ignore results from journal(s)")
parser.add_argument("-nc", "--nocirc",
                    help="ignore results from circulars and telegrams (GCN, IAUC, AT)",
                    action="store_true")
parser.add_argument("-y", "--year",
                    help="search ADS for abstracts with year or year range")
parser.add_argument("-k", "--known",
                    help="file with list of bibcodes already known to skip over in results")
parser.add_argument("-x", "--exclude",
                    help="file with list of bibcodes to not include in results")
parser.add_argument("-f", "--full", help="search full text instead just abstract and title",
                    action="store_true")
parser.add_argument("-ns", "--nosearch", help="Do not perform a search: convert known bibcode to HTML reference list only",
                    action="store_true")
parser.add_argument("-t", "--template", help="Create a master bibliography template page",
                    action="store_true")

# read arguments from the command line
args = parser.parse_args()

# check for --version or -V
if args.version:
    print("This is run_ads_query version %s" % (VERSION))
    sys.exit(0)

# Exclude request journals if irrelevant (e.g. GCN and AT notices)
if args.reject_journal:
    if ',' in args.reject_journal:
        condensed = args.reject_journal.replace(' ', '')
        reject_journals = condensed.split(',')
    else:
        reject_journals = [args.reject_journal]
else:
    reject_journals = []

# Reject circulars and telegrams if requested
if args.nocirc:
    for items in circulars:
        reject_journals.append(items)

if not args.mission:
    print("WARNING: no mission name provided, assuming CALET")
    args.mission = 'calet'

# Default to searching to mission name in title and abstract if no
# search term or terms provided
if args.search:
    if ',' in args.search:
        include_terms = args.search.split(',')
    else:
        include_terms = [ args.search ]
else:
    include_terms = [ args.mission ]
glue = '\" OR \"'
core = glue.join(include_terms).join(('(\"', '\")'))

if args.reject_search:
    if ',' in args.reject_search:
        reject_terms = args.reject_search.split(',')
    else:
        reject_terms = [ args.reject_search ]
    neg_core = glue.join(reject_terms).join(('(\"', '\")'))
    core += ' AND NOT ' + neg_core
    abs_query = 'abs:(' + core + ') '
    full_query = 'body:(' + core + ') -:' + neg_core + ' '
else:
    abs_query = 'abs:(' + core + ') '
    full_query = 'body:(' + core + ') '
    
# Default to searching all years if not set
if args.year:
    year_query = 'year:' + args.year + ' '
else:
    year_query = ''

# If there have been prior searches already documented, we do not need to see them
# again: skip over them if a list of known bibcodes is provided, and search for
# "mission_name"_known_bibcodes.txt if no other list name provided
if args.known:
    if args.known == 'none' or args.known == 'None' or args.known == 'NONE':
        existing_file = ''
    else:
        existing_file = args.known
else:
    existing_file = args.mission + '_known_bibcodes.txt'
known_bibcodes = []
try:
    with open(existing_file, 'r') as bibfile:
        known_bibcodes = bibfile.read().splitlines()
    bibfile.close()
    print("Found %d already known references" % (len(known_bibcodes)))
except:
    print("No file", existing_file, "found with already known references")
    
# Remove invalid bibcodes (such as blank lines)
prior_bibcode = 'FIRST LINE'
for bibcode in known_bibcodes:
    if len(bibcode) != 19:
        print("Rejecting known invalid bibcode \'%s\' after \'%s\' in %s" % (bibcode, prior_bibcode, existing_file))
        known_bibcodes.remove(bibcode)
    else:
        prior_bibcode = bibcode
        
# If there have been prior searches with known irrelevant results (e.g. papers
# on plate tectonics while searching for astronomy results), filter them out.
# Defaults to looking for "mission_name"_exclude_bibcodes.txt if no
# filename for irrelevant bibcodes provided.
if args.exclude:
    if args.exclude == 'none' or args.exclude == 'None' or args.exclude == 'NONE':
        existing_file = ''
    else:
        existing_file = args.exclude
else:
    existing_file = args.mission + '_exclude_bibcodes.txt'
reject_bibcodes = []
try:
    with open(existing_file, 'r') as bibfile:
        reject_bibcodes = bibfile.read().splitlines()
    bibfile.close()
    print("Exluding %d known undesired references" % (len(reject_bibcodes)))
except:
    print("No file", existing_file, "found with known references to skip")

# Remove invalid bibcodes (such as blank lines)
prior_bibcode = 'FIRST LINE'
for bibcode in reject_bibcodes:
    if len(bibcode) != 19:
        print("Rejecting invalid bibcode \'%s\' after \'%s\' in %s" % (bibcode, prior_bibcode, existing_file))
        reject_bibcodes.remove(bibcode)
    else:
        prior_bibcode = bibcode

# Run the code twice: once for refereed journals, a second time for all other
# references.
# Store the results in seperate |-delimited ASCII and ordered HTML lists for
# each case. Do the refereed search first, then search all results while
# skipping over the already-found refereed results on the second time around
today_code = date.today().strftime("%Y%m%d")
ref_flag = [True, False]
complete_bibcodes = []

# Split mission name into "mission #" if the mission has a name with a number
# (e.g. "venera14" becomes "venera 14", while "ogo" becomes "ogo")
mission_parts = text_num_split(args.mission)
if mission_parts == None:
    mission_name = args.mission
else:
    mission_name = "%s %s" % (mission_parts[0], mission_parts[1])

for refereed in ref_flag:
    if refereed:
        ref_query = 'property:refereed '
        results_file = args.mission + '_refereed_' + today_code + '.txt'
        html_file = args.mission + '_refereed.html'
        biblio_html_file = args.mission + '_biblio_refereed.html'
        new_file = args.mission + '_refereed_new.html'
    else:
        ref_query = ''
        results_file = args.mission + '_nonrefereed_' + today_code + '.txt'
        html_file = args.mission + '_nonrefereed.html'
        biblio_html_file = args.mission + '_biblio_nonrefereed.html'
        new_file = args.mission + '_nonrefereed_new.html'

    prior_results = []
    if len(known_bibcodes):
        # Break up queries into groups of 50 bibcodes per search to 
        # prevent overwhelming the search field while not having to 
        # do a seperate query for each bibcode
        N = 50
        sublist = [known_bibcodes[n:n+N] for n in range(0, len(known_bibcodes), N)]
        for group in sublist:
            glue = ' OR '
            core = glue.join(group).join(('(', ')'))
            query_string = 'bibcode:' + core + ' ' + ref_query
            # Some existing bibcodes might be in the exlude list: remove them
            partial_results = bib_query(query_string, reject_bibcodes, [])
            for single_result in partial_results:
                prior_results.append(single_result)
                complete_bibcodes.append(single_result['bibcode'])
                reject_bibcodes.append(single_result['bibcode'])
    else:
        if args.nosearch:
            print("No prior known results and no search requested: you get nothing")

    if args.full:
        query_string = full_query + year_query + ref_query + 'collection:astronomy'
        print("Query: %s" % (query_string))
        full_results = bib_query(query_string, reject_bibcodes, reject_journals)
        print("%d additional full text references found" % len(full_results))
        for full_codes in full_results:
            reject_bibcodes.append(full_codes['bibcode'])
            complete_bibcodes.append(full_codes['bibcode'])
    else:
        full_results = []

    if args.nosearch:
        print("No search requested, converting known bibcodes to HTML references")
        results = prior_results
        new_results = []
    else:    
        query_string = abs_query + year_query + ref_query + 'collection:astronomy'
        print("Query: %s" % (query_string))
        abs_results = bib_query(query_string, reject_bibcodes, reject_journals)
        print("%d additional references found" % len(abs_results))
        for abs_codes in abs_results:
            reject_bibcodes.append(abs_codes['bibcode'])
            complete_bibcodes.append(abs_codes['bibcode'])
        results = full_results
        results.extend(abs_results)
        new_results = results.copy()
        results.extend(prior_results)
    # Sort into reverse chronological order by year, then in regular order by
    # journal name, page, etc.
    results.sort(key=lambda item: item.get("bibcode"))
    new_results.sort(key=lambda item: item.get("bibcode"))
    results.sort(reverse=True, key=lambda item: item.get("year"))
    new_results.sort(reverse=True, key=lambda item: item.get("year"))
    
    # Write the result to plain text with bibcodes, and again as a complete
    # HTML list, and finally as an HTML list for only the new references found
    # (v 0.83 addition: write a standard HEASARC bibliography page with
    # all required headers, titles, links, and footers)
    print("Writing results into %s and %s" % (results_file, html_file))
    with open(results_file, 'w') as bibfile:
        for paper in results:
            bibfile.write(paper['bibcode'] + '\n')
        bibfile.close()

    with open(results_file, 'w') as bibfile:
        for paper in results:
            if paper['author'] == None:
                author_string = ''
            else:
                author_string = ';'.join(paper['author_norm'])
            bib_bits = [
                paper['bibcode'],
                author_string,
                paper['title'],
                str(paper['citation_count'])
                ]
            bibstring = '|'.join(bib_bits) + '\n'
            bibfile.write(bibstring)
    bibfile.close()

    if len(results) > 0:
        listing = bibcode_to_htmllist(results)
        if (refereed):
            ref_type = 'Refereed Journals'
        else:
            ref_type = 'Non-refereed Publications'
        print("Writing %s" % (biblio_html_file)) 
        f = open(biblio_html_file, 'w')
        f.write('<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n')
        f.write('<title>%s Bibliography (%s)</title>\n' % (mission_name.upper(), ref_type))
        f.write('</head>\n\n<body>\n\n')
        f.write('<!--================================================================-->\n\n')
        f.write('<!--#include virtual="/docs/obsheader.html"-->\n\n')
        f.write('<!--================================================================-->\n\n')
        f.write('<hr>\n<h2>%s %s</h2>\n<hr><p>\n\n' % (mission_name.capitalize(), ref_type))
        f.write('<ol>\n')
        f.write(listing)
        f.write('</ol>\n\n')
        f.write('<!--================================================================-->\n')
        f.write('<hr>\n\n<center>\n')
        f.write('    <b><a href=\"/docs/heasarc/missions/%s.html\">\n' % (args.mission))
        f.write('    [%s]</a></b>\n' % (mission_name.capitalize()))
        f.write('    <b><a href=\"/docs/heasarc/missions/biblio/%s_biblio.html\">\n' % (args.mission))
        f.write('    [Bibliography]</a></b>\n')
        f.write('</center>\n\n')
        f.write('<!--================================================================-->\n\n')
        f.write('<!--#include virtual=\"/docs/heasarc/missions/missions_footer.html\"-->\n\n')
        f.write('<!--================================================================-->\n\n')
        f.write('<!--#include virtual=\"/docs/corp/obsbuttons.html\"-->\n\n')
        f.write('<!--================================================================-->\n\n')
        f.write('<!--#include virtual=\"/docs/corpfooter.html\"-->\n\n')
        f.write('</body>\n</html>\n')
        f.close()
    else:
        print("No references found, so %s not made" % (html_file))

    if len(new_results):
        print("Writing new-found results into %s" % (new_file))
        f = open(new_file, 'w')
        f.write('<!DOCTYPE html>\n<html>\n<body>\n\n')
        f.write('<ol>\n')
        listing = bibcode_to_htmllist(new_results)
        f.write(listing)
        f.write('</ol>\n\n</body>\n</html>\n')
        f.close()
    else:
        print("No new results were found, not making %s" % (new_file))

if args.template:
    biblio_html_file = args.mission + '_biblio_template.html'
    print("Writing %s" % (biblio_html_file)) 
    f = open(biblio_html_file, 'w')
    f.write('<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n')
    f.write('<title>%s Bibliography</title>\n' % (mission_name.upper()))
    f.write('</head>\n\n<body>\n\n')
    f.write('<!--================================================================-->\n\n')
    f.write('<!--#include virtual="/docs/obsheader.html"-->\n\n')
    f.write('<!--================================================================-->\n\n')
    f.write('<hr>\n<h2>%s Publications</h2>\n' % (mission_name.capitalize()))
    f.write('<hr><p>\n\n')
    f.write('<!--================================================================-->\n\n')
    f.write('[IMAGE of mission goes here]\n\n')
    f.write('<h3><i><img alt=\"*\" src=\"/Images/heasarc/icons/orangeball.gif\">\n')
    f.write('    <font color=#cc6600>%s Publications</font></i></h3>\n\n' % (mission_name.capitalize()))
    f.write('<p>The %s publication list through [DATE] is the result\n' % (mission_name.capitalize()))
    f.write('of a query to the <a href=\"https://ui.adsabs.harvard.edu/\">ADS service</a>\n')
    f.write('using the keyword &ldquo;%s&rdquo;.</p>\n\n' % (mission_name))
    f.write('<ul>\n<li><a href=\"/docs/heasarc/missions/biblio/%s_biblio_refereed.html\">\n' % (args.mission))
    f.write('    Refereed journals</a></li>\n')
    f.write('<li><a href=\"/docs/heasarc/missions/biblio/%s_biblio_nonrefereed.html\">\n' % (args.mission))
    f.write('    Non-refereed publications</a></li>\n</ul>\n\n')
    f.write('<h3><i><img alt=\"*\" src=\"/Images/heasarc/icons/orangeball.gif\">\n')
    f.write('    <font color=#cc6600>Useful %s references</font></i></h3>\n\n' % (mission_name.capitalize()))
    f.write('[REFERENCES GO HERE]\n\n<ul>\n</ul>\n\n')
    f.write('<!--================================================================-->\n')
    f.write('<hr>\n\n<center>\n')
    f.write('    <b><a href=\"/docs/heasarc/missions/%s.html\">\n' % (args.mission))
    f.write('    [%s]</a></b>\n' % (mission_name.capitalize()))
    f.write('    <b><a href=\"/docs/heasarc/missions/biblio/%s_biblio.html\">\n' % (args.mission))
    f.write('    [Bibliography]</a></b>\n')
    f.write('</center>\n\n')
    f.write('<!--================================================================-->\n\n')
    f.write('<!--#include virtual=\"/docs/heasarc/missions/missions_footer.html\"-->\n\n')
    f.write('<!--================================================================-->\n\n')
    f.write('<!--#include virtual=\"/docs/corp/obsbuttons.html\"-->\n\n')
    f.write('<!--================================================================-->\n\n')
    f.write('<!--#include virtual=\"/docs/corpfooter.html\"-->\n\n')
    f.write('</body>\n</html>\n')
    f.close()

if (len(complete_bibcodes) and not args.nosearch):
    temp_bibcodes = []
    for bibcode in complete_bibcodes:
        year = bibcode[0:4]
        revised_entry = {
            'year': year,
            'bibcode': bibcode
            }
        temp_bibcodes.append(revised_entry)
    temp_bibcodes.sort(key=lambda item: item.get("bibcode"))
    temp_bibcodes.sort(reverse=True, key=lambda item: item.get("year"))
    bibcode_file = args.mission + '_known_bibcodes_' + today_code + '.txt'
    print('Writing %s\n' % (bibcode_file))
    with open(bibcode_file, 'w') as bibfile:
        for reference in temp_bibcodes:
            bibfile.write(reference['bibcode'] + '\n')        
    bibfile.close()
elif not args.nosearch:
    print("Failed to find any results, past or present: this is suspicious!")
