README
26 October 2026
Jesse Allen

CONTENT

README.md        This file

mission pages/   Python code using flask to read .json format templates
                 and generate a large set of HTML files to a standard
		 design

plots/           Automated matplotlib-generated charts to show the temporal
                 and energy range coverage of 150+ high energy astrophysics missions.
		 

biblio/          Python code, HTML output pages, and ADS bibcode result tracking
                 for automated updates of publication records


ogip-validator/  UNDER DEVELOPEMENT
                 Set up using harbor format to use an AI agent to read technical
		 documents and generate FITS format validation for data to be
		 ingested in compliance with formal requirements (standard OGIP
		 specifications plus unique mission requirements).
		 Contains instructions for AI agent and known working solution for
		 validating accuracy

PURPOSE

Mission pages.

The HEASARC maintains a "complete" history of all missions that carried high energy
astrophysics detectors that generated known data. These pages were originally created in
raw HTML, but suffered some style drift with different authors over many years. In order
to simplify this and give all pages a modern common style such as the use of USWDS classes,
these pages were broken down into component parts (lanuch date, the presence of data in
the HEASARC, energy range, instrumentation details, etc.) and saved in JSON format.
Using python code and the flask library, developed a series of templates to rapidly
deploy multiple possible designs for review and selection: code here reflects only
this final model.

.json collection here should be complete and accurate as of late October 2026.


Plots

The HEASARC also maintains graphical charts showing all missions and providing plots
of these, including future mission, with both temporal and energy ranges. In order to
make updating these charts simple, code was written to read the .json files made
for mission pages and generate static plots: new mission additions or corrections would
be made to the .json files to update mission page, then no new work other than re-running
the code would be necessary to update the charts.


Bibliography page updates

Astronomy missions' purpose is publication, and new discoveries with missions are
constantly being made, especially for current and recent mission data analysis.
Code here uses the standard ADS python query libraries to search for recent papers
for missions with keyword searches, and to automate HTML publication lists. The
code keeps track of previously obtained results to prevent duplication and, where
documented, a list of bibcode results to reject as not relevant (e.g. results about
a ground-based instrument with the same name as a space-based one)


ICD and OGIP FITS Validator

EXPERIMENTAL! These pages are largely placeholders for code in devlopment. The
intention here is two fold:

  * Using standard harbor format setup, provide the necessary set up and structure to
    request an AI agent be created that reads the OGIP standards (settings that all
    FITS lightcurves, images, etc. must follow to be compliant with NASA stadnardds and
    work correctly in all software) and mission-specific settings as documented for
    each individual mission in their Interface Control Document (ICD) or Technical
    Agreement.
    The goal is an agent that can read these documents, create FITS validation template,
    and execute it correctly: as new missions develop or ICDs are updated, the agent
    can autonomous update the templates and verify new and existing data files for
    the changed standard, and report on issues.
    Initially this was developed to support a code challenge (developing a real world
    computation task that AI agents cannot perform unsupervised), but the ultimate
    goal is a working, not a failing, solution

  * Given its initial intent as a code challenge for AI agents, an existing trusted
    solution is also provided for grading: the trusted solution is not self-updated
    (Changes to the ICD need to be propogated to the template, and the archive
    re-scanned), but is suitable for grading purposes