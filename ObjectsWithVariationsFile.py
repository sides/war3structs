from construct import *
from structs.common import *

"""
  Formats: w3d, w3a, w3q

  The objects with variations file is exactly the same as the objects
  file, but contains a variation parameter to specify what level of the
  ability or upgrade is being modified, or which variation of a doodad.
"""

ObjectModificationWithVariation = Struct(
  "modification_id" / Byte[4],
  "variable_type" / Enum(Integer, INT=0, REAL=1, UNREAL=2, STRING=3),
  "variation" / Integer,
  "value" / Switch(this.variable_type.type, {
    "INT" : Integer,
    "REAL" : Float,
    "UNREAL" : Float,
    "STRING" : String
  }),
  "ability_pointer" / Integer,
  "end" / Integer
)

ObjectDefinitionWithVariation = Struct(
  "original_object_id" / Byte[4],
  "new_object_id" / Byte[4],
  "modifications_count" / Integer,
  "modifications" / Array(this.modifications_count, ObjectModificationWithVariation)
)

ObjectTableWithVariation = Struct(
  "objects_count" / Integer,
  "objects" / Array(this.objects_count, ObjectDefinitionWithVariation)
)

ObjectsWithVariationsFile = Struct(
  "version" / Integer,
  "original_objects_table" / ObjectTableWithVariation,
  "custom_objects_table" / ObjectTableWithVariation
)
