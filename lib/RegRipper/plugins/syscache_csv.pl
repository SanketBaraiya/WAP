#-----------------------------------------------------------
# syscache_csv.pl 
#   
# Change history
#   20200515 - updated date output format
#   20190425 - csv output added
#   20181209 - original plugin created
#
# References
#   https://github.com/libyal/winreg-kb/blob/master/documentation/SysCache.asciidoc
#
# Copyright 2020 QAR, LLC
# Author: H. Carvey, keydet89@yahoo.com
#-----------------------------------------------------------
package syscache_csv;
use strict;

my %config = (hive          => "syscache",
              hasShortDescr => 0,
              hasDescr      => 0,
              hasRefs       => 0,
              osmask        => 22,
              category      => "program execution",
              version       => 20200515);
my $VERSION = getVersion();

# Functions #
sub getConfig {return %config}
sub getHive {return $config{hive};}
sub getVersion {return $config{version};}
sub getDescr {}
sub getShortDescr {}
sub getRefs {}

sub pluginmain {
	my $class = shift;
	my $hive = shift;
#	
#  ::rptMsg("syscache_csv v.".$VERSION); 
#  ::rptMsg("(".$config{hive}.") ".getShortDescr()."\n");     
	my $reg = Parse::Win32Registry->new($hive);
	my $root_key = $reg->get_root_key;
	my $key;

  my $key_path = 'DefaultObjectStore\\ObjectTable';
  if ($key = $root_key->get_subkey($key_path)) {
  	my @subkeys = $key->get_list_of_subkeys();
  	if (scalar @subkeys > 0) {
  		foreach my $sk (@subkeys) {
  			processKey($sk);
#  			::rptMsg("");
  		}
  	}
  	
  }
  else {
  	::rptMsg($key_path." not found");
  }
}

sub processKey {
	my $key = shift;
	my @str = ();
	my $lw = $key->get_timestamp();
#	::rptMsg("LastWrite: ".gmtime($lw)." Z");
	push(@str,::getDateFromEpoch($lw)."Z");
	
	eval {
		my ($f1,$f2,$seq) = unpack("Vvv",$key->get_value("_FileId_")->get_data());
		my $entry = mftRecNum($f1,$f2);
#		::rptMsg("  FileID         = ".$entry."/".$seq);
		push(@str,$entry."/".$seq);
	};
	
	
	eval {
		my $aefileid = $key->get_value("AeFileID")->get_data();
		$aefileid =~ s/\00//g;
		my $sha1 = $aefileid;
		$sha1 =~ s/^0000//;
		push(@str,$sha1);
#		::rptMsg("  AeFileID       = ".$aefileid);
#		::rptMsg("  SHA-1 Hash     = ".$sha1);
	};
	
#	eval {
#		my ($u1,$u2) = unpack("VV",$key->get_value("_UsnJournalId_")->get_data());
#		my $usn = ::getTime($u1,$u2);
#		::rptMsg("  USN Journal ID = ".gmtime($usn)." Z");	
#	};
	my $s = join(',',@str);
	::rptMsg($s);
}

# from: http://www.cse.scu.edu/~tschwarz/coen252_07Fall/Lectures/NTFS.html
# "Each MFT record is addressed by a 48 bit MFT entry value.The first entry has address 0. 
# Each MFT entry has a 16 bit sequence number that is incremented when the entry is allocated. 
# MFT entry value and sequence number combined yield 64b file reference address.:
#
# The 64-bit field is translated as 48-bits for the entry number and 16-bits for the 
# sequence number
#
# variation of the below code shared by David Cowen
sub mftRecNum {
	my $f1 = shift;
	my $f2 = shift;
	
	if ($f2 == 0) {
		return $f1;
	}
	else {
		$f2 = ($f2 * 16777216);
		return ($f1 + $f2);
	}
}

1;