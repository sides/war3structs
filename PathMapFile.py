from construct import *
from structs.common import *

"""
  Formats: wpm

  The path map file describes the pathing in a map.
"""

PathMapHeader = Struct(
  "file_id" / Const(b"MP3W"),
  "version" / Integer,
  "path_map_width" / Integer,
  "path_map_height" / Integer
)

PathPoint = FlagsEnum(Byte,
  can_walk   = 0x02,
  can_fly    = 0x04,
  can_build  = 0x08,
  is_blight  = 0x20,
  is_ground  = 0x40, # or water
  is_unknown = 0x80
)

PathMapFile = Struct(
  "header" / PathMapHeader,
  "data" / Array(this.header.path_map_width * this.header.path_map_height, PathPoint)
)
