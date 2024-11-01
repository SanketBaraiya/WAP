#-----------------------------------------------------------
# runvirtual.pl
#   
#
# Change history
#   20200427 - updated output date format
#   20191211 - created
#
# References
#   https://docs.microsoft.com/en-us/microsoft-desktop-optimization-pack/appv-v5/running-a-locally-installed-application-inside-a-virtual-environment-with-virtualized-applications
#
# Copyright 2020 QAR, LLC 
# Author: H. Carvey, keydet89@yahoo.com
#-----------------------------------------------------------
package runvirtual;
use strict;

my %config = (hive          => "NTUSER\.DAT, Software",
              hasShortDescr => 1,
              hasDescr      => 0,
              hasRefs       => 0,
              osmask        => 22,
              category      => "persistence",
              version       => 20200427);
my $VERSION = getVersion();

sub getConfig {return %config}
sub getHive {return $config{hive};}
sub getVersion {return $config{version};}
sub getDescr {}
sub getShortDescr {
	return "Gets RunVirtual entries";
}
sub getRefs {}

sub pluginmain {
	my $class = shift;
	my $hive = shift;
	
  ::rptMsg("runvirtual v.".$VERSION); 
  ::rptMsg("(".$config{hive}.") ".getShortDescr()."\n"); 
	my $reg = Parse::Win32Registry->new($hive);
	my $root_key = $reg->get_root_key;
	my $key;
	
	my @paths = ("Software\\Microsoft\\AppV\\Client\\RunVirtual",
	             "Microsoft\\AppV\\Client\\RunVirtual");
	             
	foreach my $key_path (@paths) {
		if ($key = $root_key->get_subkey($key_path)) {

			::rptMsg($key_path);
			::rptMsg("LastWrite Time ".::getDateFromEpoch($key->get_timestamp())."Z");
			::rptMsg("");
			
			my @subkeys = $key->get_list_of_subkeys();
			if (scalar @subkeys > 0) {
				foreach my $s (@subkeys) {
					my $name = $s->get_name();
					my $lw   = $s->get_timestamp();
					::rptMsg("RunVirtual: ".$name."  LastWrite: ".::getDateFromEpoch($lw)."Z");
					eval {
						my $def = $s->get_value("")->get_data();
						::rptMsg("Default value = ".$def);
					};
				}
			}
			else {
				::rptMsg($key_path." has no subkeys\.");
			}
		}
		else {
#			::rptMsg($key_path." not found\.");
		}
	} 
}

1;
