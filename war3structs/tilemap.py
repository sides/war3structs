from construct import *
from .common import *

"""
  Formats: w3e
  Version: 11

  The tile map file contains the map's tile and cliff data.
"""

TilesetEnum = Enum(Byte,
  ASHENVALE       = ord("A"),
  BARRENS         = ord("B"),
  FELWOOD         = ord("C"),
  DUNGEON         = ord("D"),
  LORDAERONFALL   = ord("F"),
  UNDERGROUND     = ord("G"),
  LORDAERONSUMMER = ord("L"),
  NORTHREND       = ord("N"),
  VILLAGEFALL     = ord("Q"),
  VILLAGE         = ord("V"),
  LORDAERONWINTER = ord("W"),
  DALARAN         = ord("X"),
  CITYSCAPE       = ord("Y"),
  SUNKENRUINS     = ord("Z"),
  ICECROWN        = ord("I"),
  DALARANRUINS    = ord("J"),
  OUTLAND         = ord("O"),
  BLACKCITADEL    = ord("K")
)

TilePoint = Bitwise(Struct(
  "ground_height" / Bytewise(Short),
  "water_level" / Bytewise(Short),
  "flags" / FlagsEnum(Nibble,
    boundary_flag_first  = 0x4000,
    ramps                = 0x0010,
    use_blight_default   = 0x0020,
    water_enabled        = 0x0040,
    boundary_flag_second = 0x0080
  ),
  "ground_texture_type" / Nibble,
  "texture_details" / Octet,
  "cliff_texture_type" / Nibble,
  "layer_height" / Nibble
))

TileMapFile = Struct(
  "file_id" / Const(b"W3E!"),
  "version" / Integer,
  "tileset_id" / TilesetEnum,
  "custom_tilesets" / Integer,
  "ground_tileset_ids_count" / Integer,
  "ground_tileset_ids" / Array(this.ground_tileset_ids_count, ByteId),
  "cliff_tileset_ids_count" / Integer,
  "cliff_tileset_ids" / Array(this.cliff_tileset_ids_count, ByteId),
  "tile_map_width" / Integer,
  "tile_map_height" / Integer,
  "tile_map_center_offset_x" / Float,
  "tile_map_center_offset_y" / Float,
  "tile_map" / Array(this.map_width * this.map_height, TilePoint)
)
