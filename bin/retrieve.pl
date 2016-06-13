
# quick script to call the REST interface at ADS to pull the data we want over
#
# NOTE: You'll need to supply a key where it sez KEY_HERE below
# obtain this from the ADS
#

my $result = "results.json";

open (BIBCODE, $ARGV[0]);

foreach my $bibcode (<BIBCODE>) 
{
   chomp $bibcode;
   $bibcode =~ s/^\s+//;
   $bibcode =~ s/\s+$//;
   my $cmd = "curl -H 'Authorization: Bearer:KEY_HERE' 'http://api.adsabs.harvard.edu/v1/search/query?q=bibcode:".$bibcode."&fl=abstract,keyword' >> ".$result."; echo , >> ".$result;
   system $cmd;
}

print "FINISHED\n";

close FILE;
