from construct import *
from .common import *

"""
  Formats: w3x

  The map file is the structure of maps themselves. They are just MPQs
  with a special header and footer.
"""

MapFlags = FlagsEnum(Integer,
  preview_screen_hide_minimap         = 0x0001,
  modify_ally_priorities              = 0x0002,
  is_melee_map                        = 0x0004,
  is_large_map                        = 0x0008, # ?
  masked_area_partially_visible       = 0x0010,
  fixed_player_settings_custom_forces = 0x0020,
  use_custom_forces                   = 0x0040,
  use_custom_techtree                 = 0x0080,
  use_custom_abilities                = 0x0100,
  use_custom_upgrades                 = 0x0200,
  map_properties_menu_first_open      = 0x0400, # ?
  cliff_shores_show_water_waves       = 0x0800,
  rolling_shores_show_water_waves     = 0x1000,
  use_terrain_fog                     = 0x2000,
  unknown_flag_1                      = 0x4000, # ?
  use_item_classification_system      = 0x8000
)

MapHeader = Padded(512, Struct(
  "file_id" / Const(b"HM3W"),
  "placeholder" / Integer,
  "name" / String,
  "flags" / MapFlags,
  "players_count" / Integer
))

MapFooter = Struct(
  "sign_id" / Const(b"NGIS"),
  "authentication" / Byte[256]
)

MapFile = Struct(
  "header" / MapHeader,
  "mpq" / GreedyBytes
)
