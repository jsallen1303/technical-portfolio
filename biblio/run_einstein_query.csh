#!/bin/tcsh
#
# HEAO 2 (HEAO-B before launch, and also more often called the 
# Einstein X-ray Observatory) is a bit of a tangled mess: the 
# moniker Einstein gets hung on many many concepts, some of them in 
# Astrophysics, many of them quite unrelated to the X-ray observatory.
# The search terms below attempt to automatically eliminate most of the 
# more obvious and common wrong matches (e.g. by excluding journals 
# which only have cosmology or quantum gravity results), but there's a 
# LOT of weeding to do even then (einstein_exclude_bibcodes.txt has
# about 1000 references that made it through the filters below, and any new 
# updated search will need to add more). Things to look for:
# a) Albert Einstein (bibliographies, centennary celebrations from 2005 for 
#    for the "miracle year" of 1905 when Albert did too much publishing and 
#    not enough sorting of the Swiss Post)
# b) History papers on relativity (e.g. the precession of Mercury's perihelion)
# c) Contemporary work on special and general relativity testing 
#    (frame dragging tests with modern satellites, for example)
# d) Spectroscopy related to Einstein A coefficients (which comes up as 
#    astronomy in the context of OH masers)
# e) Bose-Einstein condensates (How these are astronomy papers, I do not 
#    know: the ADS categorizations may not be flawless)
# f) Weird, but fun, stuff. My favorite? Ed Regis' book "Who Got Einstein's
#    Office?" (as not to spoil the plot, but the answer is Stromgen)
# g) HEAO 1 and HEAO 3 papers which do not refer at all the HEAO 2 or HEAO B
#    (likely some quirk of search in ADS)
# h) The proposed Beyond Einstein Probe mission (to test a number of aspects
#    of relativity predictions). This is often shortened to "Einstein Probe"
#    or (more unfortunately for our search) "the Einstein mission" (as if there
#    had not already been one).
# Suffice it to say there is a great deal of manual sifting and even now, 
# additional misnomers to be found. 

run_ads_query_html.py --mission einstein --search "Einstein,HEAO-2,HEAO-B" \
  --reject_journal "CQGra,JMP,IJMPA,IJMPD,PhRv,PhRvA,PhRvD,PhRvL,JGP,EPJC,GReGr" \
  --reject_search "Albert Einstein,Riemann,Maxwell,Cartan,Klein,Gordon,Gauss,Bonnet,Boltzmann,Dirac,Stokes,Born,Infeld,Yang,Mills,Vlasov,Bose,deSitter,Sitter,Hilbert,Higgs,Schwartzchild,spacetime,lensing,Equivalence,Einstein equations,gravity,aether,Einstein A coefficient,universe,equation of state,strange star,quark,dark matter,maser,tensor,Einstein Probe,field equation,Einstein ring,Einstein cross,inflaton,planet,holography,relativity,relativistic,perfect fluid,HEAO 1,HEAO 3" \
  --known einstein_known_bibcodes_20180221.txt
