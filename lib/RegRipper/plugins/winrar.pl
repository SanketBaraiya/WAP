#-----------------------------------------------------------
# winrar.pl
# Get WinRAR\ArcHistory entries
#
# History
#   20200526 - updated date output format
#   20080819 - created
#
#
# copyright 2020 Quantum Analytics Research, LLC
# author: H. Carvey, keydet89@yahoo.com
#-----------------------------------------------------------
package winrar;
use strict;

my %config = (hive          => "NTUSER\.DAT",
              osmask        => 22,
              hasShortDescr => 1,
              hasDescr      => 0,
              hasRefs       => 0,
              version       => 20200526);

sub getConfig{return %config}

sub getShortDescr {
	return "Get WinRAR\\ArcHistory entries";	
}
sub getDescr{}
sub getRefs {}
sub getHive {return $config{hive};}
sub getVersion {return $config{version};}

my $VERSION = getVersion();

sub pluginmain {
	my $class = shift;
	my $hive = shift;
	
	::rptMsg("winrar v.".$VERSION); # banner
    ::rptMsg("(".getHive().") ".getShortDescr()."\n"); # banner
	my $reg = Parse::Win32Registry->new($hive);
	my $root_key = $reg->get_root_key;

	my $key_path = "Software\\WinRAR\\ArcHistory";
	my $key;
	if ($key = $root_key->get_subkey($key_path)) {
		::rptMsg("WinRAR");
		::rptMsg($key_path);
		::rptMsg("LastWrite Time ".::getDateFromEpoch($key->get_timestamp())."Z");
		::rptMsg("");
		
		my %arc;
		my @vals = $key->get_list_of_values();
		if (scalar(@vals) > 0) {
			foreach my $v (@vals) {
				$arc{$v->get_name()} = $v->get_data();
			}
			
			foreach (sort keys %arc) {
				::rptMsg($_." -> ".$arc{$_});
			}
			
		}
		else {
			::rptMsg($key_path." has no values.");
		}
	}
	else {
		::rptMsg($key_path." not found.");
	}
}
1;