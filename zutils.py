from __future__ import print_function
from pprint import pprint
import traceback
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

def dbg(*x):
	"""Crude debug-println which includes the calling function name
	"""
	print(traceback.extract_stack()[-2][-2],end=": ")
	pprint(x)
