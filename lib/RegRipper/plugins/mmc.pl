#-----------------------------------------------------------
# mmc.pl
# Plugin for Registry Ripper, NTUSER.DAT edition - gets the 
# Microsoft Management Console Recent File List values 
#
# Change history
#   20200517 - updated date output format
#   20080324 - created
#
# References
#
# 
# copyright 2020 Quantum Analytics Research, LLC
# Author: H. Carvey, keydet89@yahoo.com
#-----------------------------------------------------------
package mmc;
use strict;

my %config = (hive          => "NTUSER\.DAT",
              hasShortDescr => 1,
              hasDescr      => 0,
              hasRefs       => 0,
              osmask        => 22,
              version       => 20200517);

sub getConfig{return %config}
sub getShortDescr {
	return "Get contents of user's MMC\\Recent File List key";	
}
sub getDescr{}
sub getRefs {}
sub getHive {return $config{hive};}
sub getVersion {return $config{version};}

my $VERSION = getVersion();

sub pluginmain {
	my $class = shift;
	my $ntuser = shift;
	
	::rptMsg("mmc v.".$VERSION); # banner
    ::rptMsg("(".getHive().") ".getShortDescr()."\n"); # banner
	my $reg = Parse::Win32Registry->new($ntuser);
	my $root_key = $reg->get_root_key;

	my $key_path = 'Software\\Microsoft\\Microsoft Management Console\\Recent File List';
	my $key;
	if ($key = $root_key->get_subkey($key_path)) {
		::rptMsg("MMC - Recent File List");
		::rptMsg($key_path);
		::rptMsg("LastWrite Time ".::getDateFromEpoch($key->get_timestamp())."Z");
		my @vals = $key->get_list_of_values();
		if (scalar(@vals) > 0) {
			my %files;
# Retrieve values and load into a hash for sorting			
			foreach my $v (@vals) {
				my $val = $v->get_name();
				my $data = $v->get_data();
				my $tag = (split(/File/,$val))[1];
				$files{$tag} = $val.":".$data;
			}
# Print sorted content to report file			
			foreach my $u (sort {$a <=> $b} keys %files) {
				my ($val,$data) = split(/:/,$files{$u},2);
				::rptMsg("  ".$val." -> ".$data);
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