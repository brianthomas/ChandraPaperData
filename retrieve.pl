
my $result = "results.json";

open (BIBCODE, $ARGV[0]);

foreach my $bibcode (<BIBCODE>) 
{
   chomp $bibcode;
   $bibcode =~ s/^\s+//;
   $bibcode =~ s/\s+$//;
   my $cmd = "curl -H 'Authorization: Bearer:YSzSGbTuwW9jNmZF9XxYEnaOpk9ewTDqAiLWEic2' 'http://api.adsabs.harvard.edu/v1/search/query?q=bibcode:".$bibcode."&fl=abstract,keyword' >> ".$result."; echo , >> ".$result;
   system $cmd;
}

print "FINISHED\n";

close FILE;
