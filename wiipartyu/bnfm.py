from ..core import *

BNFMFormat = StructField([
	["FOURCC", StringField(Value(4))],
])

def getFormat():
	return WMB3Format.copy()