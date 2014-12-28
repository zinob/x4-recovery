#!/usr/bin/python
#FAT32 code mostly based on:
# https://www.pjrc.com/tech/8051/ide/fat32.html

import struct
from zutils import dbg,list_to_struct,pretty_unpack

def main():
	import doctest
	doctest.testmod()

def test_header():
	"""
	>>> mydisk=FAT("/home/zinob/Projekt/filmrec/buncofiles.dd")
	>>> mydisk.get_fat_chain(2)==[2]
	True
	>>> mydisk.get_fat_chain(39)==[39,40]
	True
	"""

def test_naive_file_read():
	"""
	>>> mydisk=FAT("/home/zinob/Projekt/filmrec/buncofiles.dd")
	>>> cowfile=[i["DIR_FstClus"] for i in mydisk.rootdir if i["DIR_Name"].startswith("MOOH")][0]
	>>> cowfile
	39
	>>> mydisk=FAT("/home/zinob/Projekt/filmrec/buncofiles.dd")
	>>> fileblob=mydisk.read_fat_chain(cowfile)
	>>> len(fileblob)==8192
	True
	>>> fileblob.startswith("1the techno goes boom")
	True
	>>> fileblob[4899:4911]=='uhnts uhnts\\n'
	True
	"""

def test_dir_content():
	"""
	>>> mydisk=FAT("/home/zinob/Projekt/filmrec/buncofiles.dd")
	>>> len(mydisk.rootdir)
	24
	>>> rootset=set([i["DIR_Name"].strip() for i in mydisk.rootdir])
	>>> ref=set(['BAR','COW','MOOH','FOO']).union(str(i) for i in range(1,21))
	>>> ref==rootset
	True
	>>> mydisk.get_dir([])==mydisk.rootdir
	True
	>>> subdir=[i["DIR_Name"].strip() for i in mydisk.get_dir(["FOO"])]
	>>> set(subdir)==set(['.', '..', 'XYZ', 'ZYX'])
	True
	>>> mydisk.get_dir(["doesnotexist,shouldfail"])
	Traceback (most recent call last):
	...
	KeyError: 'Directory "DOESNOTEXIST,SHOULDFAIL" not found'

	HorribleFailure
	"""
class FAT(object):
	"""Represents a FAT32 file-system as an object"""
	def __init__(self, diskfile):
		self.disk=open(diskfile,"rb")
		self.header=self.parse_fat_header(self.disk.read(0x200))

		self.rootdir=self.read_dir(self.header["BPB_RootClus"])
		
	def get_dir(self,pathlist):
		"""
		returns the content of a specified directory
		for an example directory of /foo/bar/ the pathlist should be
		["foo","bar"]
		returns the content of the requested directory
		"""
		return self.__r_get_dir(pathlist,self.rootdir)

	def __r_get_dir(self, pathlist, start):
		if pathlist==[]:
			return start
		ctarget=pathlist[0].upper()
		for entry in start:
			ename=entry["DIR_Name"].strip().upper()
			eaddr=entry["DIR_FstClus"]
			if ctarget==ename:
				if entry["DIR_Attr"]["isDict"]:
					return self.__r_get_dir(pathlist[1:],self.read_dir(eaddr))
					
		else:
			raise KeyError('Directory "%s" not found'%ctarget)

	def read_dir(self,sector):
		"""Reads the content of a directory starting at sector
		returns a list of the content, as per parse_object"""
		struct=self.read_fat_chain(sector)
		return self.parse_dir(struct)

	def parse_dir(self,binstruct):
		"""Expects a raw-directory listing,
		returns a list of items as per parse_object"""
		files=[]
		for i in range(0,len(binstruct),32):
			cRecord=self.parse_object(binstruct[i:i+32])
			if cRecord["TYPE"]=="normal":
				files.append(cRecord)
		return files

	def read_fat_chain(self,start):
		h=self.header
		f=self.disk
		secPerClus=h["BPB_SecPerClus"]
		bytsPerSec=h["BPB_BytsPerSec"]
		bytesPerClus=secPerClus*bytsPerSec

		firstDataSector=h["BPB_RsvdSecCnt"] + (h["BPB_NumFATs"] * h["BPB_FATSz32"])
		firstSectorofCluster  = ((start -2)*secPerClus)+firstDataSector
		addr=firstSectorofCluster*bytsPerSec
		obuff=""
		for i in self.get_fat_chain(start):
			firstSectorofCluster  = ((i -2)*secPerClus)+firstDataSector
			addr=firstSectorofCluster*bytsPerSec
			f.seek(addr)
			obuff+=f.read(bytesPerClus)
		return obuff

	def get_fat_chain(self,start):
		"""Takes a starting cluster,
		returns a list of the clusters associated with that file"""
		chain=[start]
		f=self.disk
		fatHeader=self.header

		while True:
			assert chain[-1]!=0, "Null-pointer in record"
			next=self.read_FAT_pos(chain[-1])
			if next < 0xffffff8:
				chain.append(next)
			else:
				return chain
			

	def read_FAT_pos(self, pos):
		"""expects a file pointer and the associated FAT-header
		returns the FAT as a list"""
		f=self.disk
		h=self.header
		f.seek(h["BPB_RsvdSecCnt"]*h["BPB_BytsPerSec"]+4*pos)
		fatSize=h["BPB_FATSz32"]*h["BPB_BytsPerSec"]
		addr=f.read(4)
		return struct.unpack("<L",addr)[0]

	def parse_object(self,record):
		"""parses a 32 byte long directory item
		 returns it as a dictionary containing the most essensial records.
		"""
		dictStruct=[
			{"desc":"Short Filename", "abbrv":"DIR_Name",
				"len":11,"type":"string","sig":False},
			{"desc":"Attrib Byte", "abbrv":"DIR_Attr",
				"type":"byte","sig":False},
			 {"desc":"Padding", "abbrv":"","len":8,"type":"pad"},
			{"desc":"First Cluster High", "abbrv":"DIR_FstClusHI",
				"type":"short","sig":False},
			 {"desc":"Padding", "abbrv":"","len":4,"type":"pad"},
			{"desc":"First Cluster Low", "abbrv":"DIR_FstClusLO",
				"type":"short","sig":False},
			{"desc":"File Size", "abbrv":"DIR_FileSize",
				"type":"int","sig":False},
		]
		unpacked=pretty_unpack(dictStruct,record)


		unpacked["DIR_FstClus"]=unpacked["DIR_FstClusHI"]*2**16+unpacked["DIR_FstClusLO"]

		attr=unpacked["DIR_Attr"]
		unpacked["DIR_Attr"]=self.parse_dir_attr(unpacked["DIR_Attr"])
		
		if attr&15==15:
			unpacked["TYPE"]="longname"
		elif unpacked["DIR_Name"][0]=="\0":
			unpacked["TYPE"]="end"
		elif unpacked["DIR_Name"][0]=="\xe5":
			unpacked["TYPE"]="deleted"
		else:
			unpacked["TYPE"]="normal"
		#Normal record with short filename - Attrib is normal
		#Long filename text - Attrib has all four type bits set
		#Unused - First byte is 0xE5
		#End of directory - First byte is zero 
		return unpacked

	def parse_dir_attr(self,attrByte):
		"""Takes a single attribute-byte for a directory item 
		returns a dict of boolean attributes
		"""
		bitmap=[bool(attrByte>>i&1) for i in range(8)]
		names=["RO","Hidden","isSystem","isVolID","isDict","Archived","MBZ","MBZ"]
		return dict(zip(names,bitmap))

	def parse_fat_header(self,header):
		"""parses a 512 byte long string and parses
		it as a FAT-file-system header block
		returns a dict containing the most essensial data-fields"""

		headStruct=[
			{"desc":"Padding", "abbrv":"",
				"len":11,"type":"pad","sig":False},
			{"desc":"Bytes/Sector=512", "abbrv":"BPB_BytsPerSec",
				"type":"short","sig":False},
			{"desc":"Sectors/Cluster", "abbrv":"BPB_SecPerClus",
				"type":"byte","sig":False},
			{"desc":"Reserved Sectors", "abbrv":"BPB_RsvdSecCnt",
				"type":"short","sig":False},
			{"desc":"Number of FATs", "abbrv":"BPB_NumFATs",
				"type":"byte","sig":False},
			{"desc":"Padding",
				"len":19,"type":"pad","sig":False},
			{"desc":"Sectors Per FAT", "abbrv":"BPB_FATSz32",
				"type":"int","sig":False},
			{"desc":"Padding",
				"len":4,"type":"pad","sig":False},
			{"desc":"Directory First Cluster", "abbrv":"BPB_RootClus",
				"type":"int","sig":False},
			{"desc":"Padding",
				"len":462,"type":"pad","sig":False},
			{"desc":"Signature = 0xAA55=43605", "abbrv":"sign",
				"type":"short","sig":False}
		]
		header=pretty_unpack(headStruct,header)
		assert header["sign"]==43605, "invalid disk header"
		return header


if __name__ == "__main__":
	main()
