#!/usr/bin/python

import struct

def main():
	f=open("/home/zinob/Backups/sdcard.dd")
	header=f.read(0x200)
	list_to_struct(headStruct)
	headfmt="<"+list_to_struct(headStruct)
	headerStruct=struct.unpack_from(headfmt,header)
	titles=[i["abbrv"] for i in headStruct if i["type"]!="pad"]
	headerData=dict(zip(titles,headerStruct))
	h=headerData
	cluster_begin_lba=h["BPB_RsvdSecCnt"] + (h["BPB_NumFATs"] * h["BPB_FATSz32"])
	sectors_per_cluster = h["BPB_SecPerClus"]
	root_dir_first_cluster = h["BPB_RootClus"]


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

def list_to_struct(list):
	"""Takes a list of dicts of the format
	[{
		len:bytes,
		type:["byte"|"short"|"int"|"long"|"longlong"|"float"|"padding"],
		sig:Bool
	},
	...]
	and converts it to a python struct-fmt string"""
	obuff=""
	types={"pad":"x","byte":"b", "short":"h", "int":"i", "long":"l", "longlong":"q"}
	for i in list:
		token=str(i.get("len",""))
		token+=types[i["type"]]
		if (not token[-1] in "x") and not i["sig"]:
			token=token.upper()
		else:
			token=token.lower()

		obuff+=token
	return obuff


main()
