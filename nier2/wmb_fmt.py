from ..core import *

def BlockEntryField():
	return FieldGroup([
		["offset", Uint32Field()],
		["count", Uint32Field()],
	])

WMB3Format = FieldGroup([
	["FOURCC", StringField(Value(4))],
	["version", Uint32Field()],
	["dummy", Uint32Field()],
	["flags", Uint32Field()],
	["bounding_box", FieldGroup([
		["x", FloatField()],
		["y", FloatField()],
		["z", FloatField()],
		["w", FloatField()],
		["h", FloatField()],
		["d", FloatField()],
	])],
	
	["isize", VarField(
		If(
			Equals(BitwiseAnd(GetField("flags"), Value(8)), Value(0)),
			Value(2),
			Value(4),
		)
	)],
	
	["blockEntryList", FieldGroup([
		["boneEntry", BlockEntryField()],
		["unk1Entry", BlockEntryField()],
		["geoEntry", BlockEntryField()],
		["subMeshEntry", BlockEntryField()],
		["lodEntry", BlockEntryField()],
		["unk2Entry", BlockEntryField()],
		["boneMapEntry", BlockEntryField()],
		["boneSetEntry", BlockEntryField()],
		["matEntry", BlockEntryField()],
		["meshGroupEntry", BlockEntryField()],
		["meshGrpMatEntry", BlockEntryField()],
		["unk3Entry", BlockEntryField()],
	])],
	
	["boneInfoList", FarBlock(
		GetField("blockEntryList/boneEntry/offset"),
		ArrayField(
			GetField("blockEntryList/boneEntry/count"),
			FieldGroup([
				["boneId", Uint16Field()],
				["parentIdx", Int16Field()],
				["local_pos", Vector3Field()],
				["local_rot", Vector3Field()],
				["local_scale", Vector3Field()],
				["world_pos", Vector3Field()],
				["world_rot", Vector3Field()],
				["world_scale", Vector3Field()],
				["world_position_tpos", Vector3Field()],
			])
		)
	)],
	
	["unk1List", FarBlock(
		GetField("blockEntryList/unk1Entry/offset"),
		ArrayField(
			GetField("blockEntryList/unk1Entry/count"),
			Uint8Field(),
		)
	)],
	
	["geoList", FarBlock(
		GetField("blockEntryList/geoEntry/offset"),
		ArrayField(
			GetField("blockEntryList/geoEntry/count"),
			FieldGroup([
				
				["vbOffsetList", ArrayField(
					Value(4),
					Uint32Field(),
				)],
				["vbStrideList", ArrayField(
					Value(4),
					Uint32Field(),
				)],
				["vnum", Uint32Field()],
				["vfmt", Uint32Field()],
				["ibOffset", Uint32Field()],
				["inum", Uint32Field()],
				["vbList", ArrayField(
					Value(4),
					IfField(
						Equals(GetField("vbOffsetList[{I}]"), Value(0)),
						NullField(),
						FarBlock(
							GetField("vbOffsetList[{I}]"),
							RawData(Mul(
								GetField("vnum"),
								GetField("vbStrideList[{I}]"),
							)),
						)
					)
				)],
				["ib", FarBlock(
					GetField("ibOffset"),
					RawData(Mul(GetField("inum"), GetField("isize"))),
				)],
			]),
		)
	)],
	
	["subMeshList", FarBlock(
		GetField("blockEntryList/subMeshEntry/offset"),
		ArrayField(
			GetField("blockEntryList/subMeshEntry/count"),
			FieldGroup([
				["geoIdx", Uint32Field()],
				["bonesetIdx", Int32Field()],
				["vstart", Uint32Field()],
				["istart", Uint32Field()],
				["vnum", Uint32Field()],
				["inum", Uint32Field()],
				["primNum", Uint32Field()],
			])
		)
	)],	
	
	["lodList", FarBlock(
		GetField("blockEntryList/lodEntry/offset"),
		ArrayField(
			GetField("blockEntryList/lodEntry/count"),
			FieldGroup([
				["nameOffset", Uint32Field()],
				["name", FarBlock(
					GetField("nameOffset"),
					NullTerminatedStringField(),
				)],
				["lodLevel", Int32Field()],
				["submeshInfoStart", Uint32Field()],
				["submeshInfoOffset", Uint32Field()],
				["submeshInfoNum", Uint32Field()],
				
				["submeshInfoList", FarBlock(
					GetField("submeshInfoOffset"),
					ArrayField(
						GetField("submeshInfoNum"),
						FieldGroup([
							["geoIndex", Uint32Field()],
							["meshGroupIndex", Uint32Field()],
							["matIndex", Uint32Field()],
							["unk0", Int32Field()],
							["meshGroupMatPairIndex", Uint32Field()],
							["unk1", Int32Field()],
						])
					),
				)],
			]),
		),
	)],
	
	["bonemap", FarBlock(
		GetField("blockEntryList/boneMapEntry/offset"),
		ArrayField(
			GetField("blockEntryList/boneMapEntry/count"),
			Uint32Field(),
		)
	)],
	
	["boneSetList", FarBlock(
		GetField("blockEntryList/boneSetEntry/offset"),
		ArrayField(
			GetField("blockEntryList/boneSetEntry/count"),
			FieldGroup([
				["offset", Uint32Field()],
				["count", Uint32Field()],
				["boneIndexList", FarBlock(
					GetField("offset"),
					ArrayField(
						GetField("count"),
						Uint16Field(),
					)
				)]
			])
		)
	)],
	
	["matList", FarBlock(
		GetField("blockEntryList/matEntry/offset"),
		ArrayField(
			GetField("blockEntryList/matEntry/count"),
			FieldGroup([
				["unk0", Uint16Field()],
				["unk1", Uint16Field()],
				["unk2", Uint16Field()],
				["unk3", Uint16Field()],
				["materialNameOffset", Uint32Field()],
				["effectNameOffset", Uint32Field()],
				["techniqueNameOffset", Uint32Field()],
				["unk7", Uint32Field()],
				["samplerOffset", Uint32Field()],
				["samplerNum", Uint32Field()],
				["unk10", Uint32Field()],
				["unk11", Uint32Field()],
				["varOffset", Uint32Field()],
				["varNum", Uint32Field()],
				
				["materialName", FarBlock(
					GetField("materialNameOffset"),
					NullTerminatedStringField(),
				)],
				["effectName", FarBlock(
					GetField("effectNameOffset"),
					NullTerminatedStringField(),
				)],
				["techniqueName", FarBlock(
					GetField("techniqueNameOffset"),
					NullTerminatedStringField(),
				)],
				["samplerList", FarBlock(
					GetField("samplerOffset"),
					ArrayField(
						GetField("samplerNum"),
						FieldGroup([
							["nameOffset", Uint32Field()],
							["textureHash", Uint32Field()],
							["name", FarBlock(
								GetField("nameOffset"),
								NullTerminatedStringField(),
							)]
						])
					)
				)],
				["varList", FarBlock(
					GetField("varOffset"),
					ArrayField(
						GetField("varNum"),
						FieldGroup([
							["nameOffset", Uint32Field()],
							["value", FloatField()],
							["name", FarBlock(
								GetField("nameOffset"),
								NullTerminatedStringField(),
							)]
						])
					)
				)],
			])
		)
	)],
	
	["meshGroupList", FarBlock(
		GetField("blockEntryList/meshGroupEntry/offset"),
		ArrayField(
			GetField("blockEntryList/meshGroupEntry/count"),
			FieldGroup([
				["nameOffset", Uint32Field()],
				["boundingBox", FieldGroup([
					["x", FloatField()],
					["y", FloatField()],
					["z", FloatField()],
					["w", FloatField()],
					["h", FloatField()],
					["d", FloatField()],
				])],
				["offset2", Uint32Field()],
				["n2", Uint32Field()],
				["offset3", Uint32Field()],
				["n3", Uint32Field()],
				
				["name", FarBlock(
					GetField("nameOffset"),
					NullTerminatedStringField(),
				)],
				["data2", FarBlock(
					GetField("offset2"),
					ArrayField(
						GetField("n2"),
						Uint16Field(),
					)
				)],
				["data3", FarBlock(
					GetField("offset3"),
					ArrayField(
						GetField("n3"),
						Uint16Field()
					)
				)]
			])
		)
	)],
	
	["meshGrpMatList", FarBlock(
		GetField("blockEntryList/meshGrpMatEntry/offset"),
		ArrayField(
			GetField("blockEntryList/meshGrpMatEntry/count"),
			ArrayField(
				Value(2),
				Uint32Field()
			)
		)
	)],
])

def getFormat():
	return WMB3Format.copy()