#-----------------------------------------------------------
# secrets.pl
# Get the last write time for the Policy\Secrets key
# 
#
# History
#   20200517 - updated date output format
#   20140730 - created
#
# Note: When gsecdump.exe is run with the "-a" switch, or the LSA
#       secrets are dumped, the tool accesses the Policy\Secrets key
#       in a way that modifies the key LastWrite time without changing
#       any values or data.  As such, the LastWrite time of this key may
#       correlate to the time that gsecdump.exe was run.  Insight for this
#       plugin was provided by Jamie Levy
#
# copyright 2020 Quantum Analytics Research, LLC
# Author: H. Carvey, keydet89@yahoo.com
#-----------------------------------------------------------
package secrets;
use strict;

my %config = (hive          => "Security",
              hasShortDescr => 1,
              hasDescr      => 0,
              hasRefs       => 0,
              osmask        => 22,
              version       => 20200517);

sub getConfig{return %config}
sub getShortDescr {
	return "Get the last write time for the Policy\\Secrets key";	
}
sub getDescr{}
sub getRefs {}
sub getHive {return $config{hive};}
sub getVersion {return $config{version};}

my $VERSION = getVersion();

sub pluginmain {
	my $class = shift;
	my $hive = shift;
	
	::rptMsg("secrets v.".$VERSION); # banner
  ::rptMsg("(".$config{hive}.") ".getShortDescr()."\n"); # banner
	my $reg = Parse::Win32Registry->new($hive);
	my $root_key = $reg->get_root_key;

	my $key_path = "Policy\\Secrets";
	my $key;
	if ($key = $root_key->get_subkey($key_path)) {
		::rptMsg($key_path);
		::rptMsg("LastWrite Time ".::getDateFromEpoch($key->get_timestamp())."Z");
		::rptMsg("");

	}
	else {
		::rptMsg($key_path." not found.");
	}
}

1;