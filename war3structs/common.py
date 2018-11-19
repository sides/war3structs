from construct import *

Integer = Int32sl
Short = Int16sl
Float = Float32l
String = CString("utf8")

class ByteStringAdapter(Adapter):
  def _decode(self, obj, context, path):
    return bytes(obj)

  def _encode(self, obj, context, path):
    return list(obj)

ByteId = ByteStringAdapter(Byte[4])

class BooleanAdapter(Adapter):
  def __init__(self, subcon, falseval=0, trueval=1):
    super(BooleanAdapter, self).__init__(subcon)
    self.falseval = falseval
    self.trueval = trueval

  def _decode(self, obj, context, path):
    return obj != self.falseval

  def _encode(self, obj, context, path):
    return self.trueval if obj else self.falseval

IntegerBoolean = BooleanAdapter(Integer)

Color = Struct(
  "r" / Byte,
  "g" / Byte,
  "b" / Byte,
  "a" / Byte
)

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
