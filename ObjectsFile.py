from construct import *
from structs.common import *

"""
  Formats: w3u, w3t, w3b, w3h
  Version: 1

  The objects file contains data that the object editor would typically
  manipulate. If dealing with abilities, doodads or upgrades, the
  ObjectsWithVariationsFile is used instead.
"""

ObjectModification = Struct(
  "modification_id" / Byte[4],
  "variable_type" / Enum(Integer, INT=0, REAL=1, UNREAL=2, STRING=3),
  "value" / Switch(this.variable_type.type, {
    "INT" : Integer,
    "REAL" : Float,
    "UNREAL" : Float,
    "STRING" : String
  }),
  "end" / Integer
)

ObjectDefinition = Struct(
  "original_object_id" / Byte[4],
  "new_object_id" / Byte[4],
  "modifications_count" / Integer,
  "modifications" / Array(this.modifications_count, ObjectModification)
)

ObjectTable = Struct(
  "objects_count" / Integer,
  "objects" / Array(this.objects_count, ObjectDefinition)
)

ObjectsFile = Struct(
  "version" / Integer,
  "original_objects_table" / ObjectTable,
  "custom_objects_table" / ObjectTable
)
