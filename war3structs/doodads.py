from construct import *
from .common import *

"""
  Formats: doo
  Version: 8

  The doodads file describes trees and other destructibles and doodads
  present on the map.
"""

DoodadItemSet = Struct(
  "items_count" / Integer,
  "items" / Array(this.items_count, Struct(
    "item_id" / ByteId, # this can use the "random item id" type of id
                        # see the UnitDoodadRandomUnit struct
    "chance_percent" / Integer
  ))
)

DoodadVisibilityFlags = Enum(Byte,
  INVISIBLE_NONSOLID = 0,
  VISIBLE_NONSOLID = 1,
  VISIBLE_SOLID = 2,
  OUT_OF_BOUNDS = 3 # ?
)

Doodad = Struct(
  "doodad_id" / ByteId,
  "variation" / Integer,
  "pos_x" / Float,
  "pos_y" / Float,
  "pos_z" / Float,
  "rotation" / Float, # in radians
  "scale_x" / Float,
  "scale_y" / Float,
  "scale_z" / Float,
  "visibility" / DoodadVisibilityFlags,
  "life_percent" / Byte, # -1 for doodads
  "dropped_item_table_index" / Integer, # -1 for no item drop from the map item tables
  "dropped_item_sets_count" / Integer, # only if above is -1
  "dropped_item_sets" / Array(this.dropped_item_sets_count, DoodadItemSet),
  "index" / Integer
)

# Special doodads that create terrain on the map so they must be edited
# with the terrain palette in the editor, not the doodad palette. Doing
# this presumably turns them into data in the environment file instead.
TerrainDoodad = Struct(
  "doodad_id" / ByteId,
  "pos_z" / Integer, # ? (always 0)
  "pos_x" / Integer, # ?
  "pos_y"/ Integer # ?
)

DoodadsFile = Struct(
  "file_id" / Const(b"W3do"),
  "version" / Integer,
  "subversion" / Integer, # ?
  "doodads_count" / Integer,
  "doodads" / Array(this.doodads_count, Doodad),
  "terrain_doodads_version" / Integer,
  "terrain_doodads_count" / Integer,
  "terrain_doodads" / Array(this.terrain_doodads_count, TerrainDoodad)
)
