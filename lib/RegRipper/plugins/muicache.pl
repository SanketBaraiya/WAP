
#-----------------------------------------------------------
# muicache.pl
# Plugin for Registry Ripper, NTUSER.DAT edition - gets the 
# MUICache values 
#
# Change history
#  20200525 - updated date output format, removed alertMsg() functionality
#  20130425 - added alertMsg() functionality
#  20120522 - updated to collect info from Win7 USRCLASS.DAT
#
# 
# copyright 2020 Quantum Research Analytics, LLC
# Author: H. Carvey, keydet89@yahoo.com
#-----------------------------------------------------------
package muicache;
use strict;

my %config = (hive          => "NTUSER\.DAT,USRCLASS\.DAT",
              hasShortDescr => 1,
              hasDescr      => 0,
              hasRefs       => 0,
              osmask        => 22,
              version       => 20200525);

sub getConfig{return %config}
sub getShortDescr {
	return "Gets EXEs from user's MUICache key";	
}
sub getDescr{}
sub getRefs {}
sub getHive {return $config{hive};}
sub getVersion {return $config{version};}

my $VERSION = getVersion();

sub pluginmain {
	my $class = shift;
	my $ntuser = shift;
	
	::rptMsg("muicache v.".$VERSION);
    ::rptMsg("(".getHive().") ".getShortDescr()."\n");
	my $reg = Parse::Win32Registry->new($ntuser);
	my $root_key = $reg->get_root_key;
	my $key_path = 'Software\\Microsoft\\Windows\\ShellNoRoam\\MUICache';
	my $key;
	if ($key = $root_key->get_subkey($key_path)) {
		::rptMsg($key_path);
		::rptMsg("LastWrite Time ".::getDateFromEpoch($key->get_timestamp())."Z");
		my @vals = $key->get_list_of_values();
		if (scalar(@vals) > 0) {
			foreach my $v (@vals) {
				my $name = $v->get_name();
				next if ($name =~ m/^@/ || $name eq "LangID");
				my $data = $v->get_data();
				::rptMsg("  ".$name." (".$data.")");
			}
		}
		else {
			::rptMsg($key_path." has no values.");
		}
	}
	else {
		::rptMsg($key_path." not found.");
		::rptMsg("");
	}
# Added for access to USRCLASS.DAT
	my $key_path = 'Local Settings\\Software\\Microsoft\\Windows\\Shell\\MUICache';
	my $key;
	if ($key = $root_key->get_subkey($key_path)) {
		::rptMsg($key_path);
		::rptMsg("LastWrite Time ".::getDateFromEpoch($key->get_timestamp())."Z");
		::rptMsg("");
		my @vals = $key->get_list_of_values();
		if (scalar(@vals) > 0) {
			foreach my $v (@vals) {
				my $name = $v->get_name();
				next if ($name =~ m/^@/ || $name eq "LangID");
				my $data = $v->get_data();
				::rptMsg($name." (".$data.")");
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