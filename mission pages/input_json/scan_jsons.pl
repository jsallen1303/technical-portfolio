#!/usr/bin/perl
use strict;
use warnings;

my $directory = $ARGV[0] || '.';
opendir(my $dh, $directory) or die "Cannot open $directory: $!";

foreach my $file (grep { /\.json$/ } readdir($dh)) {
    open(my $fh, '<', "$directory/$file") or next;
    my $content = do { local $/; <$fh> };
    close($fh);
    
    if ($content =~ /"navigation"\s*:\s*\[\s*\{\s*"url"\s*:\s*"[^"]+"\s*,\s*"text"\s*:\s*"([^"]+)"/ 
        && $1 =~ /More about/i) {
        print "$file\n";
    }
}
closedir($dh);
