#!/usr/bin/python

# Copyright Simon Albinsson 2014
# This software is licensed under the GPL v3 license.
# While I think GPL v3 is a bit to restrictive in the
# views that there is only one kind of "true freedom"
# I _really_ dislike DRM.

from zutils import pretty_unpack,dbg
import struct
import crudefat

def main():
	args=getargs()
	f=crudefat.FAT(args["tfile"])
	readlen=args["overread"]
	bytesPerCluster=f.header['BPB_SecPerClus']* f.header['BPB_BytsPerSec']
	candidates=[]
	for i in f.get_dir(["DCIM","100DSCIM"]):
		fname=i['DIR_Name'].strip().upper()
		if i['DIR_FileSize'] <= bytesPerCluster and fname.endswith("AVI"):
			candidates.append(i)
	of=open(i['DIR_Name'][:-3].strip()+"over"+str(readlen)+".avi","wb")
	for candidate in candidates:
		candidateClusters=f.get_fat_chain(candidate["DIR_FstClus"],naive=True)
		if candidateClusters[-1]==0:
			candidateClusters[-1]=candidateClusters[-2]+1
		for c in range(candidateClusters[0],candidateClusters[0]+readlen):
			of.write(f.read_cluster(c))
		bytesWritten=len(candidateClusters)*bytesPerCluster
		of.seek(4)
		of.write(struct.pack("<I",bytesWritten-8))
		of.seek(16)
		of.write(magicBlob)

def getargs():
	"""will use the argparse command if I ever get around to it...
	"""
	import sys
	d={}
	#d["tfile"]=sys.argv()[1]
	#nvm, lets just hardcode things for now
	d["tfile"]='sdcard.dd'
	d["overread"]=9900
	return d
	
magicBlob="""
C8\x00\x00\x00\x68\x64\x72\x6C\x61\x76\x69\x68\x38\x00\x00\x00\x9C\x82\x00\x00\x18\x3D\x35\x00\x00\x00\x00\x00\x10\x00\x00\x00\x4C\x06\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x18\x3D\x35\x00\x00\x05\x00\x00\xD0\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x4C\x49\x53\x54\x7C\x00\x00\x00\x73\x74\x72\x6C\x73\x74\x72\x68\x40\x00\x00\x00\x76\x69\x64\x73\x4D\x4A\x50\x47\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x9C\x82\x00\x00\x40\x42\x0F\x00\x00\x00\x00\x00\x4C\x06\x00\x00\x18\x3D\x35\x00\x10\x27\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\xD0\x02\x00\x00\x00\x00\x00\x00\x00\x00\x73\x74\x72\x66\x28\x00\x00\x00\x28\x00\x00\x00\x00\x05\x00\x00\xD0\x02\x00\x00\x01\x00\x18\x00\x4D\x4A\x50\x47\x00\x30\x2A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x4A\x55\x4E\x4B
"""

if __name__ == "__main__":
	main()
