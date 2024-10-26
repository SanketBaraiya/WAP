#-----------------------------------------------------------
# snapshot_viewer.pl
#   Extracts Recent File List for Microsoft Snapshot Viewer
#
# Change history
#   20110830 [fpi] + banner, no change to the version number
#
# References
#
# copyright (c) 2011-02-10 Brendan Coles <bcoles@gmail.com>
#-----------------------------------------------------------
# Require #
package snapshot_viewer;
use strict;

# Declarations #
my %config = (hive          => "NTUSER\.DAT",
              hasShortDescr => 1,
              hasDescr      => 0,
              hasRefs       => 1,
              osmask        => 22,
              version       => 20110210);
my $VERSION = getVersion();

# Functions #
sub getDescr {}
sub getConfig {return %config}
sub getHive {return $config{hive};}
sub getVersion {return $config{version};}
sub getShortDescr {
	return "Extracts Recent File List for Microsoft Snapshot Viewer.";
}
sub getRefs {
	my %refs = ("Microsoft Snapshot Viewer Homepage:" =>
	            "http://support.microsoft.com/kb/175274");
	return %refs;	
}

############################################################
# pluginmain #
############################################################
sub pluginmain {

	# Declarations #
	my $class = shift;
	my $hive = shift;

	# Initialize #
	
  ::rptMsg("snapshot_viewer v.".$VERSION); # 20110830 [fpi] + banner
  ::rptMsg("(".getHive().") ".getShortDescr()."\n"); # 20110830 [fpi] + banner

	my $reg = Parse::Win32Registry->new($hive);
	my $root_key = $reg->get_root_key;
	my $key;
	my $key_path = "Software\\Microsoft\\Snapshot Viewer\\Recent File List";

	# If # Microsoft Snapshot Viewer path exists #
	if ($key = $root_key->get_subkey($key_path)) {

		# Return # plugin name, registry key and last modified date #
		::rptMsg("Snapshot Viewer");
		::rptMsg($key_path);
		::rptMsg("LastWrite Time ".gmtime($key->get_timestamp())." (UTC)");
		::rptMsg("");

		# Extract # all keys from Microsoft Snapshot Viewer registry path #
		my @vals = $key->get_list_of_values();

		# If # registry keys exist in path #
		if (scalar(@vals) > 0) {

			# Extract # all key names+values for Microsoft Snapshot Viewer registry path #
			foreach my $v (@vals) {
				::rptMsg($v->get_name()." -> ".$v->get_data());
			}

		# Error # key value is null #
		} else {
			::rptMsg($key_path." has no values.");
		}

	# Error # Microsoft Snapshot Viewer isn't here, try another castle #
	} else {
		::rptMsg($key_path." not found.");
	}

	# Return # obligatory new-line #
	::rptMsg("");
}

# Error # oh snap! #
1;
