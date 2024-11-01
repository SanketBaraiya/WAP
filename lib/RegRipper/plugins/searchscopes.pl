#-----------------------------------------------------------
# searchscopes.pl
# Plugin for Registry Ripper, NTUSER.DAT edition - gets the 
# ACMru values 
#
# Change history
#   20200517 - updated date output format
#   20180406 - created (per request submitted by John McCash)
#
# References
#  https://www.online-tech-tips.com/internet-explorer-tips/change-default-search-engine-ie/
# 
# copyright 2020 QAR, LLC
# author: H. Carvey, keydet89@yahoo.com
#-----------------------------------------------------------
package searchscopes;
use strict;

my %config = (hive          => "NTUSER\.DAT",
              hasShortDescr => 1,
              hasDescr      => 0,
              hasRefs       => 0,
              osmask        => 22,
              version       => 20200517);

sub getConfig{return %config}
sub getShortDescr {
	return "Gets contents of user's SearchScopes key";	
}
sub getDescr{}
sub getRefs {}
sub getHive {return $config{hive};}
sub getVersion {return $config{version};}

my $VERSION = getVersion();

sub pluginmain {
	my $class = shift;
	my $ntuser = shift;
	
	::rptMsg("searchscopes v.".$VERSION); # banner
    ::rptMsg("- ".getShortDescr()."\n"); # banner
	my $reg = Parse::Win32Registry->new($ntuser);
	my $root_key = $reg->get_root_key;

	my $key_path = 'Software\\Microsoft\\Internet Explorer\\SearchScopes';
	my $key;
	if ($key = $root_key->get_subkey($key_path)) {
		::rptMsg("SearchScopes");
		::rptMsg($key_path);
		::rptMsg("DefaultScope: ".$key->get_value("DefaultScope")->get_data());
		::rptMsg("");
#		::rptMsg("LastWrite Time ".gmtime($key->get_timestamp())." (UTC)");
		my @subkeys = $key->get_list_of_subkeys();
		if (scalar(@subkeys) > 0) {
			foreach my $s (@subkeys) { 
				::rptMsg($s->get_name()." [".::getDateFromEpoch($s->get_timestamp())."Z]");
				eval {
					::rptMsg ("DisplayName: ".$s->get_value("DisplayName")->get_data());
				};
				
				::rptMsg("");
			}
		}
		else {
			::rptMsg($key_path." has no subkeys.");
		}
	}
	else {
		::rptMsg($key_path." not found.");
	}
}

1;