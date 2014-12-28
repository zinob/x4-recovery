#!/usr/bin/python
#all FAT32 code based on:
# https://www.pjrc.com/tech/8051/ide/fat32.html

import struct
from pprint import pprint
from zutils import dbg,list_to_struct,pretty_unpack

def main():
	f=open("/home/zinob/Projekt/filmrec/buncofiles.dd")
	mydisk=FAT("/home/zinob/Projekt/filmrec/buncofiles.dd")

	dbg(mydisk.header)
	assert False, "DEBUG DEATH"
	cluster_begin_lba=h["BPB_RsvdSecCnt"] + (h["BPB_NumFATs"] * h["BPB_FATSz32"])
	sectors_per_cluster = h["BPB_SecPerClus"]
	root_dir_first_cluster = h["BPB_RootClus"]
	#lba_addr = cluster_begin_lba + (cluster_number - 2) * sectors_per_cluster
	dirStart=(cluster_begin_lba)*h["BPB_BytsPerSec"]
	f.seek(dirStart)
	sector=read_fat_chain(f,h,2)
	pprint(parseDir(sector))
	#firstDict=parseObject(f.read(32))
	#pprint(["main",firstDict])
	dbg([[i,read_FAT_pos(f,h,i)] for i in range(15)])
	print "----"
	#pprint(["main rootdir",read_fat_chain(f,h,2)])
	#dbg(read_fat_chain(f,h,39))


class FAT(object):
	"""Represents a FAT32 file-system as an object"""
	def __init__(self, diskfile):
		self.disk=open(diskfile,"rb")
		self.header=self.parse_fat_header(self.disk.read(0x200))
		
	def readDir(sector):
		pass

	def parseDir(binstruct):
		"""Expects a raw-directory listing,
		returns a list of items as per parseObject"""
		files=[]
		for i in range(0,len(binstruct),32):
			cRecord=parseObject(binstruct[i:i+32])
			if cRecord["TYPE"]=="normal":
				files.append(cRecord)
		return files

	def read_fat_chain(f,fatHeader,start):
		h=fatHeader
		secPerClus=h["BPB_SecPerClus"]
		bytsPerSec=h["BPB_BytsPerSec"]
		byterPerClus=secPerClus*bytsPerSec

		firstDataSector=h["BPB_RsvdSecCnt"] + (h["BPB_NumFATs"] * h["BPB_FATSz32"])
		firstSectorofCluster  = ((start -2)*secPerClus)+firstDataSector
		addr=firstSectorofCluster*bytsPerSec
		obuff=""
		for i in get_fat_chain(f,fatHeader,start):
			firstSectorofCluster  = ((i -2)*secPerClus)+firstDataSector
			addr=firstSectorofCluster*bytsPerSec
			f.seek(addr)
			obuff+=f.read(byterPerClus)
		return obuff

	def get_fat_chain(f,fatHeader,start):
		"""takes a file pointer, a fat header and a starting sector,
		returns a list of the sectors associated with that file"""
		chain=[start]
		while True:
			assert chain[-1]!=0, "Null-pointer in record"
			if chain[-1] < 0xffffff8:
				chain.append(read_FAT_pos(f,fatHeader,chain[-1]))
			else:
				return chain
			

	def read_FAT_pos(f, fatHeader, pos):
		"""expects a file pointer and the associated FAT-header
		returns the FAT as a list"""
		h=fatHeader
		f.seek(h["BPB_RsvdSecCnt"]*h["BPB_BytsPerSec"]+4*pos)
		fatSize=h["BPB_FATSz32"]*h["BPB_BytsPerSec"]
		addr=f.read(4)
		return struct.unpack("<L",addr)[0]

	def parseObject(record):
		"""parses a 32 byte long dict-struct
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
		unpacked["DIR_Attr"]=parseDictAttr(unpacked["DIR_Attr"])
		
		if attr&15==15:
			unpacked["TYPE"]="long"
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

	def parseDictAttr(attrByte):
		"""Takes a single byte and parses it as an attribute-byte for a catalog
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



main()
