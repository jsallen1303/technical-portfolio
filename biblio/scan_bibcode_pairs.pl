#!/usr/bin/perl
#
# VERSION 0.0
# June 8 2020
# Jesse Allen (NASA/GSFC HEASARC)
#
# Quick code to compare two lists of bibcodes, which may be in an unsorted order, to see
# what codes are unique to each, and report on these to the user.

my @bibcode_files = ( 'exosat_known_refereed_bibcodes.txt', 
                      'exosat_prior_known_refereed_bibcodes.txt' );

my %listone;
my %listtwo;

open (my $fh, '<', $bibcode_files[0]);
while (my $bibcodes = <$fh>) {
    chomp($bibcodes);
    $listone{$bibcodes} = 1;
}
close $fh;

open ($fh, '<', $bibcode_files[1]);
while (my $bibcodes = <$fh>) {
    chomp($bibcodes);
    $listtwo{$bibcodes} = 1;
}
close $fh;

my %uniquebibcode;
for my $key (keys %listone) {
    unless (exists $listtwo{$key}) { $uniquebibcode{$key} = 1; }
}

printf "%d bibcodes unique to %s\n", scalar (keys %uniquebibcode), $bibcode_files[0];
for my $key (sort keys %uniquebibcode) {
    print "$key\n";
}

%uniquebibcode = ();
for my $key (keys %listtwo) {
    unless (exists $listone{$key}) { $uniquebibcode{$key} = 1; }
}

print"\n";
printf "%d bibcodes unique to %s\n", scalar (keys %uniquebibcode), $bibcode_files[1];
for my $key (sort keys %uniquebibcode) {
    print "$key\n";
}

