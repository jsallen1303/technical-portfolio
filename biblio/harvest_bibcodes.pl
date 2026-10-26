#!/usr/bin/perl
#
# Get lines with 'name="bibcode"' from canned ADS results and make a 
# single file, missionname_known_bibcodes.txt for all the missions

use strict;
use warnings;

my @filelist = sort glob("*_ads*.html");
my $current_mission = '';
my $first = 1;
my $fh;
for my $ads_file (@filelist) {
    print "Reading $ads_file\n";
    my @output = `cat $ads_file | grep 'name="bibcodes"'`;
    if ($#output > 0) { die "Unexpected result from cat $ads_file | grep"; }
    $ads_file =~ /^(\w+)_ads/;
    my $mission_name = $1;
    if ($mission_name ne $current_mission) {
        if ($first) { $first = 0; }
        else { close $fh; }
        $current_mission = $mission_name;
        my $bibcode_list = sprintf("%s_known_bibcodes.txt", $current_mission);
        open ($fh, '>', "$bibcode_list");
    }
    my @line = split(/\"/, $output[0]);
    my @bibcodes = split(/\;/, $line[5]);
    printf "Found %d know bibcodes to add to %s_known_bibcodes.txt\n", 
        scalar @bibcodes, $current_mission;
    for my $bibcode (@bibcodes) { print $fh "$bibcode\n"; }
}
close $fh;


    
