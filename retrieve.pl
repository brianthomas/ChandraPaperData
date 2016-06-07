
my $result = "results.json";

if ($#ARGV < 1) {
   print "need to specify 2 arguments, ADS key and bibcode filename\n";
   exit();
} 

my $key = $ARGV[0];
open (BIBCODE, $ARGV[1]);

foreach my $bibcode (<BIBCODE>) 
{
   chomp $bibcode;
   $bibcode =~ s/^\s+//;
   $bibcode =~ s/\s+$//;
   my $cmd = "curl -H 'Authorization: Bearer:".$key."' 'http://api.adsabs.harvard.edu/v1/search/query?q=bibcode:".$bibcode."&fl=abstract,keyword' >> ".$result; 
   system $cmd;
}

print "FINISHED\n";

close FILE;
