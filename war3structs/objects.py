from construct import *
from .common import *

"""
  Formats: w3u, w3t, w3b, w3h, w3d, w3a, w3q
  Version: 1

  The objects file contains data that the object editor would typically
  manipulate. If dealing with abilities, doodads or upgrades, the
  ObjectsWithVariationsFile is used instead of the ObjectsFile.
  Optionally, the ObjectsBestFitFile can be used as well which tries to
  parse the file with both formats--one should always fail when used
  with the other, so it selects whichever didn't fail. Performance
  should be really bad on this.
"""

class ObjectModificationTerminatorValidator(Validator):
  def _validate(self, obj, ctx, path):
    return obj in [b"\x00\x00\x00\x00", ctx._.new_object_id, ctx._.original_object_id]

ObjectModification = Struct(
  "modification_id" / ByteId,
  "variable_type" / Enum(Integer, INT=0, REAL=1, UNREAL=2, STRING=3),
  "value" / Switch(this.variable_type, {
    "INT" : Integer,
    "REAL" : Float,
    "UNREAL" : Float,
    "STRING" : String
  }),
  "parent_object_id" / ObjectModificationTerminatorValidator(ByteId)
)

ObjectDefinition = Struct(
  "original_object_id" / ByteId,
  "new_object_id" / ByteId,
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
  "parent_object_id" / ObjectModificationTerminatorValidator(ByteId)
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

ObjectsBestFitFile = Select(ObjectsWithVariationsFile, ObjectsFile)
