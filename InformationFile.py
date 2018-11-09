from construct import *
from structs.common import *

"""
  Formats: w3i

  The information file contains information about the map presented in
  a game lobby before the game starts, as well as the map's global unit
  and item tables (referenced by other formats).
"""

"""
This snippet below doesn't actually work because using players_count
means if the included player ids aren't perfectly linear (0-11, rather
than 0-4 + 6-11 + 14-15, for example) then it will skip certain players.
We can't detect the current players either because processing will be
done before all the players have been added, since ally priorities are
a player flag field on the player struct itself.

def get_player_flags_enum(ctx):
  # It's already been set, return immediately.
  if player_flags.flags:
    return True

  if not ctx._root.players_count:
    return False

  for i in range(0, ctx._root.players_count):
    player_flags.flags["Player%02d" % i] = 2 ** i

  return True

# Hack for a dynamic field here. player_flags is empty until
# player_flags_cond is used at least once. player_flags_cond will
# either process and then return player_flags or return player_flags
# immediately. It falls back on just an int. It would be better if
# construct had a type that's just a plain lambda, but I didn't figure
# out if it's possible.
player_flags = FlagsEnum(Integer)
player_flags_cond = IfThenElse(get_player_flags_enum, player_flags, Integer)
"""

PlayerFlags = FlagsEnum(Integer)

for i in range(0, 23):
  PlayerFlags.flags["player_%d" % i] = 2 ** i

Player = Struct(
  "id" / Integer,
  "type" / Enum(Integer,
    USER      = 1,
    COMPUTER  = 2,
    NEUTRAL   = 3,
    RESCUABLE = 4
  ),
  "race" / Enum(Integer,
    HUMAN    = 1,
    ORC      = 2,
    UNDEAD   = 3,
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
  "upgrade_id" / Byte[4],
  "level_changed" / Integer,
  "availability" / Integer
)

TechAvalabilityChange = Struct(
  "flags" / PlayerFlags,
  "tech_id" / Byte[4]
)

RandomUnitTable = Struct(
  "number" / Integer,
  "name" / String,
  "positions_count" / Integer,
  "positions" / Integer[this.positions_count],
  "units_count" / Integer,
  "units" / Array(this.units_count, Struct(
    "chance_percent" / Integer,
    "position_ids" / Byte[this._.positions_count * 4]
  ))
)

RandomItemTable = Struct(
  "number" / Integer,
  "name" / String,
  "sets_count" / Integer,
  "sets" / Array(this.sets_count, Struct(
    "items_count" / Integer,
    "items" / Array(this.items_count, Struct(
      "chance_percent" / Integer,
      "item_id" / Byte[4]
    ))
  ))
)

InformationFile = Struct(
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
  "global_weather_id" / Byte[4],
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
