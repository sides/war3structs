from construct import *
from .common import *
from .map import MapFlags
from .tilemap import TilesetEnum

"""
  Formats: w3i
  Version: 25

  The metadata file contains information about the map presented in
  a game lobby before the game starts, as well as the map's global unit
  and item tables (referenced by other formats).
"""

PlayerFlags = FlagsEnum(Integer)

for i in range(0, 24):
  PlayerFlags.flags["player_%d" % i] = 2 ** i

Player = Struct(
  "id" / Integer,
  "type" / Enum(Integer,
    USER = 1,
    COMPUTER = 2,
    NEUTRAL = 3,
    RESCUABLE = 4
  ),
  "race" / Enum(Integer,
    HUMAN = 1,
    ORC = 2,
    UNDEAD = 3,
    NIGHTELF = 4
  ),
  "fixed_start_position" / Integer,
  "name" / String,
  "start_position_x" / Float,
  "start_position_y" / Float,
  "ally_low_priority_flags" / PlayerFlags,
  "ally_high_priority_flags" / PlayerFlags
)

Force = Struct(
  "flags" / FlagsEnum(Integer,
    allied                      = 0x01,
    allied_victory              = 0x02,
    share_vision                = 0x04,
    share_unit_control          = 0x10,
    share_advanced_unit_control = 0x20
  ),
  "player_mask_flags" / PlayerFlags,
  "name" / String
)

UpgradeAvailabilityChange = Struct(
  "flags" / PlayerFlags,
  "upgrade_id" / ByteId,
  "level_changed" / Integer,
  "availability" / Integer
)

TechAvalabilityChange = Struct(
  "flags" / PlayerFlags,
  "tech_id" / ByteId
)

RandomUnitTable = Struct(
  "index" / Integer,
  "name" / String,
  "positions_count" / Integer,
  "positions" / Array(this.positions_count, Enum(Integer,
    UNITS = 0,
    BUILDINGS = 1,
    ITEMS = 2
  )),
  "units_count" / Integer,
  "units" / Array(this.units_count, Struct(
    "chance_percent" / Integer,
    "unit_ids" / Byte[this._.positions_count * 4] # this can use the "random id" type of id
                                                  # see the UnitDoodadRandomUnit struct for
                                                  # details
  ))
)

RandomItemTable = Struct(
  "index" / Integer,
  "name" / String,
  "sets_count" / Integer,
  "sets" / Array(this.sets_count, Struct(
    "items_count" / Integer,
    "items" / Array(this.items_count, Struct(
      "chance_percent" / Integer,
      "item_id" / ByteId  # this can use the "random item id" type of id
                          # see the UnitDoodadRandomUnit struct for details
    ))
  ))
)

MetadataFile = Struct(
  "version" / Integer,
  "number_of_saves" / Integer,
  "editor_version" / Integer,
  "name" / String,
  "author" / String,
  "description" / String,
  "recommended_players" / String,
  "camera_bounds" / Float[8],
  "camera_bounds_padding" / Integer[4],
  "playable_area_width" / Integer,
  "playable_area_height" / Integer,
  "flags" / MapFlags,
  "ground_type_tileset_id" / TilesetEnum,
  "loading_screen_preset_index" / Integer,
  "loading_screen_custom_path" / String,
  "loading_screen_text" / String,
  "loading_screen_title" / String,
  "loading_screen_subtitle" / String,
  "game_data_set_index" / Integer,
  "prologue_screen_path" / String,
  "prologue_screen_text" / String,
  "prologue_screen_title" / String,
  "prologue_screen_subtitle" / String,
  "terrain_fog_style" / Integer,
  "terrain_fog_start_z" / Float,
  "terrain_fog_end_z" / Float,
  "terrain_fog_density" / Float,
  "terrain_fog_color" / Color,
  "global_weather_id" / ByteId,
  "custom_sound_environment" / String,
  "custom_light_environment_tileset_id" / TilesetEnum,
  "water_color" / Color,
  "players_count" / Integer,
  "players" / Array(this.players_count, Player),
  "forces_count" / Integer,
  "forces" / Array(this.forces_count, Force),
  "upgrade_availability_changes_count" / Integer,
  "upgrade_availability_changes" / Array(this.upgrade_availability_changes_count, UpgradeAvailabilityChange),
  "tech_availability_changes_count" / Integer,
  "tech_availability_changes" / Array(this.tech_availability_changes_count, TechAvalabilityChange),
  "random_unit_tables_count" / Integer,
  "random_unit_tables" / Array(this.random_unit_tables_count, RandomUnitTable),
  "random_item_tables_count" / Integer,
  "random_item_tables" / Array(this.random_item_tables_count, RandomItemTable)
)
