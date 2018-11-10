from construct import *
from war3structs.common import *

"""
  Formats: mmp
  Version: 0

  The minimap icons file describes icons present on the minimap.
"""

MinimapIcon = Struct(
  "type" / Enum(Integer,
    GOLDMINE = 0,
    SHOP = 1,
    PLAYER = 2
  ),
  "coord_x" / Integer, # can be 16-240
  "coord_y" / Integer, # can be 16-240
  "color" / Struct(
    "b" / Byte,
    "g" / Byte,
    "r" / Byte,
    "a" / Byte
  )
)

MinimapIconsFile = Struct(
  "version" / Integer,
  "icons_count" / Integer,
  "icons" / Array(this.icons_count, MinimapIcon)
)
