#-----------------------------------------------------------
# assoc.pl
# Plugin to extract file association data from the Software hive file
# Can take considerable time to run; recommend running it via rip.exe
#
# History
# 20180117 - updated, based on input from Jean, jean.crush@hotmail.fr
# 20080815 - created
#
#
# copyright 2008 H. Carvey, keydet89@yahoo.com
#-----------------------------------------------------------
package assoc;
use strict;

my %config = (hive          => "Software,USRCLASS",
              osmask        => 22,
              hasShortDescr => 1,
              hasDescr      => 0,
              hasRefs       => 0,
              version       => 20180117);

sub getConfig{return %config}

sub getShortDescr {
	return "Get list of file ext associations";	
}
sub getDescr{}
sub getRefs {}
sub getHive {return $config{hive};}
sub getVersion {return $config{version};}

my $VERSION = getVersion();

sub pluginmain {
	my $class = shift;
	my $hive = shift;
	
	::rptMsg("assoc v.".$VERSION); # banner
  ::rptMsg("(".$config{hive}.") ".getShortDescr()."\n"); # banner
	my $reg = Parse::Win32Registry->new($hive);
	my $root_key = $reg->get_root_key;

	my @paths = ("Classes","Classes\\Wow6432Node","Wow6432Node");
	my $key;
	foreach my $key_path (@paths) { 
		if ($key = $root_key->get_subkey($key_path)) {
			::rptMsg("assoc");
			::rptMsg($key_path);
#		::rptMsg("LastWrite Time ".gmtime($key->get_timestamp())." (UTC)");
			::rptMsg("");
# First step will be to get a list of all of the file extensions
			my %ext;
			my @sk = $key->get_list_of_subkeys();
			if (scalar(@sk) > 0) {
				foreach my $s (@sk) {
					my $name = $s->get_name();
					next unless ($name =~ m/^\.\w+$/);
					my $data;
					eval {
						$data = $s->get_value("")->get_data();
					};
					if ($@) {
# Error generated, as "(Default)" value was not found					
					}
					else {
						$ext{$name} = $data if ($data ne "");
					}
				}
# Once a list of all file ext subkeys has been compiled, access the file type
# to determine the command line used to launch files with that extension
				foreach my $e (keys %ext) {
					my $cmd;
					eval {
						$cmd = $key->get_subkey($ext{$e}."\\shell\\open\\command")->get_value("")->get_data();
					};
					if ($@) {
# error generated attempting to locate <file type>.\shell\open\command\(Default) value					
					}
					else {
						::rptMsg($e." : ".$cmd);
					}
				}
			}
			else {
				::rptMsg($key_path." has no subkeys.");
			}
		}
	}
}
1;