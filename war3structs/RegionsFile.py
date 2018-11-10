from construct import *
from war3structs.common import *

"""
  Formats: w3r
  Version: 5

  The regions file contains the regions in the map.
"""

Region = Struct(
  "left" / Float, # jass coords
  "right" / Float,
  "bottom" / Float,
  "top" / Float,
  "name" / String,
  "index" / Integer,
  "weather_effect_id" / ByteId,
  "ambient_sound_variable" / String, # as per SoundsFile
  "color" / Padded(4, Struct(
    "b" / Byte,
    "g" / Byte,
    "r" / Byte
  ))
)

RegionsFile = Struct(
  "version" / Integer,
  "regions_count" / Integer,
  "regions" / Array(this.regions_count, Region)
)
