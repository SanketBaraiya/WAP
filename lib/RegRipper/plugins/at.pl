#-----------------------------------------------------------
# at.pl
# Look for Scheduled Tasks created using at.exe, in the Software hive  
#
# Change history
#   20200525 - updated date output format
#   20140821 - created
#
# 
# Copyright (c) 2020 Quantum Analystics Research,LLC
# Author: H. Carvey, keydet89@yahoo.com
#-----------------------------------------------------------
package at;
use strict;

my %config = (hive          => "Software",
              hasShortDescr => 1,
              hasDescr      => 0,
              hasRefs       => 0,
              osmask        => 22,
              category      => "program execution",
              version       =>  20200525);

my $VERSION = getVersion();

sub getConfig {return %config}
sub getHive {return $config{hive};}
sub getVersion {return $config{version};}
sub getDescr {}
sub getShortDescr {return "Checks Software hive for AT jobs";}
sub getRefs {}

sub pluginmain {
	my $class = shift;
	my $hive = shift;

	
  ::rptMsg("at v.".$VERSION); # 20110830 [fpi] + banner
  ::rptMsg("(".$config{hive}.") ".getShortDescr());   
  ::rptMsg("");  
	my $reg = Parse::Win32Registry->new($hive);
	my $root_key = $reg->get_root_key;
	my $key;
	my $key_path = 'Microsoft\\Windows NT\\CurrentVersion\\Schedule\\TaskCache\\Tree';
	
	if ($key = $root_key->get_subkey($key_path)) {
		
		my @sk = $key->get_list_of_subkeys();
		if (scalar @sk > 0) {
			foreach my $s (@sk) {
				my $name = $s->get_name();
				next unless ($name =~ m/^At/);
				my $lw = $s->get_timestamp();
				::rptMsg($name." - LastWrite time: ".::getDateFromEpoch($lw)."Z");
			}
		}
	}
	else {
		
		
	}
}

1;
