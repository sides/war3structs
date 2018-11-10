from construct import *
from .common import *

"""
  Formats: w3u, w3t, w3b, w3h
  Version: 1

  The objects file contains data that the object editor would typically
  manipulate. If dealing with abilities, doodads or upgrades, the
  ObjectsWithVariationsFile is used instead.
"""

class ObjectModificationParentIdValidator(Validator):
  def _validate(self, obj, ctx, path):
    return obj in [ctx._.new_object_id, ctx._.original_object_id]

ObjectModification = Struct(
  "modification_id" / ByteId,
  "variable_type" / Enum(Integer, INT=0, REAL=1, UNREAL=2, STRING=3),
  "value" / Switch(this.variable_type, {
    "INT" : Integer,
    "REAL" : Float,
    "UNREAL" : Float,
    "STRING" : String
  }),
  "parent_object_id" / Select(Const(0, Integer), ObjectModificationParentIdValidator(ByteId))
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
