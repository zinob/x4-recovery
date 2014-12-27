#!/usr/bin/python

import struct

def main():
	f=open("/home/zinob/Backups/sdcard.dd")
	h=parseFatHeader(f.read(0x200))

	cluster_begin_lba=h["BPB_RsvdSecCnt"] + (h["BPB_NumFATs"] * h["BPB_FATSz32"])
	sectors_per_cluster = h["BPB_SecPerClus"]
	root_dir_first_cluster = h["BPB_RootClus"]
	#lba_addr = cluster_begin_lba + (cluster_number - 2) * sectors_per_cluster
	dirStart=cluster_begin_lba*h["BPB_BytsPerSec"]
	print hex(dirStart)
	f.seek(dirStart)
	firstDict=parseDict(f.read(32))
	print(fi)

def parseDict(record):
	"""parses a 32 byte long string and parses
	it as a FAT dictionary record.
	"""
	dictStruct=[
		{"desc":"Short Filename", "abbrv":"DIR_Name",
			"len":11,"type":"string","sig":False},
		{"desc":"Attrib Byte", "abbrv":"DIR_Attr",
			"type":"byte","sig":False},
		{"desc":"First Cluster High", "abbrv":"DIR_FstClusHI",
			"type":"short","sig":False},
		{"desc":"First Cluster Low", "abbrv":"DIR_FstClusLO",
			"type":"short","sig":False},
		{"desc":"File Size", "abbrv":"DIR_FileSize",
			"type":"int","sig":False},
	]
	dictfmt="<"+list_to_struct(dictStruct)
	dictStruct=struct.unpack_from(dictfmt,record)

	titles=[i["abbrv"] for i in dictStruct if i["type"]!="pad"]
	return dict(zip(titles,dictStruct))

parse dictAttr(attrByte):
	"""Takes a single byte and parses it as an attribute-byte for a catalog
	returns a dict of boolean attributes
	"""
	bitmap=[bool(attrByte>>i&1) for i in range(8)]
	return zip(["RO","Hidden","isVolID","isDict","Archived","MBZ","MBZ"],bitmap)

def parseFatHeader(header):
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

	headfmt="<"+list_to_struct(headStruct)
	headerStruct=struct.unpack_from(headfmt,header)
	titles=[i["abbrv"] for i in headStruct if i["type"]!="pad"]
	return(dict(zip(titles,headerStruct)))

def list_to_struct(list):
	"""Takes a list of dicts of the format
	[{
		len:bytes,
		type:["byte"|"short"|"int"|"long"|"longlong"|"float"|"padding"|"string"],
		sig:Bool
	},
	...]
	and converts it to a python struct-fmt string"""
	obuff=""
	types={"pad":"x","byte":"b", "short":"h", "int":"i", "long":"l", "longlong":"q","string":"s"}
	for i in list:
		token=str(i.get("len",""))
		token+=types[i["type"]]
		if (not token[-1] in "xs") and not i["sig"]:
			token=token.upper()
		else:
			token=token.lower()

		obuff+=token
	return obuff


main()
