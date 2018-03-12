from ..core import *

BNFMFormat = StructField([
	["FOURCC", StringField(Value(4))],
	["HeaderStart", Uint32Field()],
	["Blank", Uint32Field()],
	["FaceStart", Uint32Field()],

	["FaceTotal", Uint32Field()],
	["VertCount", Uint32Field()],
	["BoneChartStart", Uint32Field()],
	["Unknown", Uint32Field()],

	["VertStart", Uint32Field()],
	["FaceStartB", Uint32Field()],
	["Unknown1", Uint32Field()],
	["PolyNameCount", Uint32Field()],
	
	["BoneCount", Uint32Field()],
	["PolyCount", Uint32Field()],
	["MatCount", Uint32Field()],
	["PolyNameCountB", Uint32Field()],
	
	["PolyNameCountC", Uint32Field()],
	["BoneChartCount", Uint32Field()],
	["BoneChartCountB", Uint32Field()],
	["StringCount", Uint32Field()],

	["UnknownStart", Uint32Field()],
	["Unknown", Uint32Field()],
	["BoneStart", Uint32Field()],
	["PolyInfoStart", Uint32Field()],
	
	["MaterialStart", Uint32Field()],
	["UnknownStart", Uint32Field()],
	["Material2Start", Uint32Field()],
	["BoneMatrixStart", Uint32Field()],
	
	["BoneMatrixStart", Uint32Field()],
	["StringStart", Uint32Field()],
	
	["BoneInfoList", FarBlock(
		GetField("BoneStart"),
		ArrayField(
			GetField("BoneCount"),
			StructField([
				["BoneNameStart", Uint32Field()],
				["BoneName", FarBlock(
					GetField("BoneNameStart"),
					CStringField(),
				)],
				["Skip1", Uint32Field()],
				["BoneParentNameStart", Uint32Field()],
				["BoneParentName", FarBlock(
					GetField("BoneParentNameStart"),
					CStringField(),
				)],
				["Skip2", StringField(Value(0x18))],
				["PosX", FloatField()],
				["PosY", FloatField()],
				["PosZ", FloatField()],
				["ScaleX", FloatField()],
				["ScaleY", FloatField()],
				["ScaleZ", FloatField()],
				["Skip3", StringField(Value(0x14))],
				["m11", FloatField()],
				["m12", FloatField()],
				["m13", FloatField()],
				["m14", FloatField()],
				["m21", FloatField()],
				["m22", FloatField()],
				["m23", FloatField()],
				["m24", FloatField()],
				["m31", FloatField()],
				["m32", FloatField()],
				["m33", FloatField()],
				["m34", FloatField()],
				["m41", FloatField()],
				["m42", FloatField()],
				["m43", FloatField()],
				["m44", FloatField()],
				["m51", FloatField()],
				["m52", FloatField()],
				["m53", FloatField()],
				["m54", FloatField()],
				["m61", FloatField()],
				["m62", FloatField()],
				["m63", FloatField()],
				["m64", FloatField()],
				["m71", FloatField()],
				["m72", FloatField()],
				["m73", FloatField()],
				["m74", FloatField()],
				["m81", FloatField()],
				["m82", FloatField()],
				["m83", FloatField()],
				["m84", FloatField()],
				["Skip4", StringField(Value(0xc))],
			])
		)
	)],
	
	["PolyInfoList", FarBlock(
		GetField("PolyInfoStart"),
		ArrayField(
			GetField("PolyCount"),
			StructField([
				["PolyNameStart", Uint32Field()],
				["PolyName", FarBlock(
					GetField("PolyNameStart"),
					CStringField(),
				)],
				["Skip1", Uint32Field()],
				["BoneChartStart", Uint32Field()],	# points to boneIDs used by this PolyInfo
				["PolyStart", Uint32Field()],
				["Skip2", StringField(Value(0x8))],
				["FaceCount", Uint32Field()],
				["PolyVertCount", Uint32Field()],
				["BoneIDCount", Uint32Field()],
				["MatID", Uint32Field()],
				["Skip3", StringField(Value(0x8))],
			])
		)
	)],
	
	["MaterialList", FarBlock(
		GetField("MaterialStart"),
		ArrayField(
			GetField("MatCount"),
			StructField([
				["MatNameStart", Uint32Field()],
				["MatName", FarBlock(
					GetField("MatNameStart"),
					CStringField(),
				)],
				["Skip1", StringField(Value(0x110))],
				["Mat2NameStart", Uint32Field()],
				["Skip2", StringField(Value(0x110))],
			]),
		),
	)],
	
	["Material2List", FarBlock(
		GetField("Material2Start"),
		ArrayField(
			GetField("MatCount"),
			StructField([
				["PolyNameStart", Uint32Field()],
				["Skip1", StringField(Value(0x38))],
			]),
		)
	)],
	
])

def getFormat():
	return WMB3Format.copy()