from construct import *
from .common import *
from .objects import ObjectModificationParentIdValidator

"""
  Formats: w3d, w3a, w3q
  Version: 1

  The objects with variations file is exactly the same as the objects
  file, but contains a variation parameter to specify what level of the
  ability or upgrade is being modified, or which variation of a doodad.
"""

ObjectModificationWithVariation = Struct(
  "modification_id" / ByteId,
  "variable_type" / Enum(Integer, INT=0, REAL=1, UNREAL=2, STRING=3),
  "variation" / Integer,
  "ability_data_column" / Enum(Integer, A=0, B=1, C=2, D=3, F=4, G=5, H=6),
  "value" / Switch(this.variable_type, {
    "INT" : Integer,
    "REAL" : Float,
    "UNREAL" : Float,
    "STRING" : String
  }),
  "parent_object_id" / Select(Const(0, Integer), ObjectModificationParentIdValidator(ByteId))
)

ObjectDefinitionWithVariations = Struct(
  "original_object_id" / ByteId,
  "new_object_id" / ByteId,
  "modifications_count" / Integer,
  "modifications" / Array(this.modifications_count, ObjectModificationWithVariation)
)

ObjectTableWithVariations = Struct(
  "objects_count" / Integer,
  "objects" / Array(this.objects_count, ObjectDefinitionWithVariations)
)

ObjectsWithVariationsFile = Struct(
  "version" / Integer,
  "original_objects_table" / ObjectTableWithVariations,
  "custom_objects_table" / ObjectTableWithVariations
)
