
#-----------------------------------------------------------
# typedurlstime.pl
# Plugin for Registry Ripper, NTUSER.DAT edition - gets the 
# TypedURLsTime values/data from Windows 8 systems
#
# Change history
#   20200526 - updated date output format
#   20120613 - created
#
# References
#   http://dfstream.blogspot.com/2012/05/windows-8-typedurlstime.html
# 
# Notes:  New entries aren't added to the key until the current
#         instance of IE is terminated.
# 
# copyright 2020 Quantum Analytics Research, LLC
# Author: H. Carvey, keydet89@yahoo.com
#-----------------------------------------------------------
package typedurlstime;
use strict;

my %config = (hive          => "NTUSER\.DAT",
              hasShortDescr => 1,
              hasDescr      => 0,
              hasRefs       => 1,
              osmask        => 22,
              version       => 20200526);

sub getConfig{return %config}
sub getShortDescr {
	return "Returns contents of user's TypedURLsTime key.";	
}
sub getDescr{}
sub getRefs {}
sub getHive {return $config{hive};}
sub getVersion {return $config{version};}

my $VERSION = getVersion();

sub pluginmain {
	my $class = shift;
	my $ntuser = shift;
	
	::rptMsg("typedurlstime v.".$VERSION); 
	::rptMsg("(".$config{hive}.") ".getShortDescr()."\n"); 
	my $reg = Parse::Win32Registry->new($ntuser);
	my $root_key = $reg->get_root_key;
	
	my $key_path = 'Software\\Microsoft\\Internet Explorer\\TypedURLsTime';
	my $key;
	if ($key = $root_key->get_subkey($key_path)) {
		::rptMsg("TypedURLsTime");
		::rptMsg($key_path);
		::rptMsg("LastWrite Time ".::getDateFromEpoch($key->get_timestamp())."Z");
		my @vals = $key->get_list_of_values();
		if (scalar(@vals) > 0) {
			my %urls;
# Retrieve values and load into a hash for sorting			
			foreach my $v (@vals) {
				my $val = $v->get_name();
				my ($t0,$t1) = unpack("VV",$v->get_data());
				my $data = ::getTime($t0,$t1);
				my $tag = (split(/url/,$val))[1];
				$urls{$tag} = $val.":".$data;
			}
# Print sorted content to report file			
			foreach my $u (sort {$a <=> $b} keys %urls) {
				my ($val,$data) = split(/:/,$urls{$u},2);
				
				my $url;
				eval {
					$url = $root_key->get_subkey('Software\\Microsoft\\Internet Explorer\\TypedURLs')->get_value($val)->get_data();
				};
				
				if ($data == 0) {
					::rptMsg("  ".$val." -> ".$data);
				}
				else {
					::rptMsg("  ".$val." -> ".::getDateFromEpoch($data)."Z (".$url.")");
				}
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