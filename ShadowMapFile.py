from construct import *
from structs.common import *

"""
  Formats: shd

  The shadow map file describes shadows on tiles.
"""

ShadowMapFile = Struct(
  "data" / GreedyRange(Enum(Byte, TRUE=0xFF, FALSE=0x00)) # the size of the file should be 16*width*height of the tilemap
)
