from construct import *
from .common import *

"""
  Formats: War3StatsObserverSharedMemory
  Version: 0

  The structure of the memory mapped observer API file. It can be read
  in-game with the mmap python module.
"""

class Utf8FallbackAdapter(Adapter):
  """Utf8FallbackAdapter class

  This adapter is necessary due to a bug in construct that fails to
  catch unicode decoding exceptions with the `Optional`, `Select`, etc
  structs. There is an issue on their tracker about it already.
  """
  def _decode(self, obj, context, path):
    try:
      return obj.decode('utf-8')
    except UnicodeDecodeError:
      return None

  def _encode(self, obj, context, path):
    try:
      return obj.encode('utf-8')
    except UnicodeEncodeError:
      return None

class FlippedByteStringAdapter(Adapter):
  def _decode(self, obj, context, path):
    return bytes(obj[::-1]).decode('utf-8')

  def _encode(self, obj, context, path):
    return list(obj.encode('utf-8'))[::-1]

FlippedByteId = FlippedByteStringAdapter(Byte[4])

ObserverPlayerResearch = Struct(
  "id" / FlippedByteId,
  Padding(100), # name
                # names are intentionally dismissed due to encoding
                # issues on different warcraft locales
                # if you need an object's name, you must get it from
                # the tables in the game data files
  "progress_percent" / Int32ul,
  "type" / Enum(Byte, UPGRADE=0, UNIT=1, REVIVAL=2),
  "art" / PaddedString(100, "utf8")
)

ObserverPlayerUnit = Struct(
  "id" / FlippedByteId,
  Padding(100), # name
  "owning_player_id" / Int32ul, # maybe?
  "alive_count" / Int32ul,
  "total_count" / Int32ul,
  "art" / PaddedString(100, "utf8"),
  "is_worker" / BooleanAdapter(Byte),
  "is_busy_worker" / BooleanAdapter(Byte),
  "damage_dealt" / Int32ul,
  "damage_received" / Int32ul,
  "damage_healed" / Int32ul
)

ObserverPlayerUpgrade = Struct(
  "id" / FlippedByteId,
  "class" / Enum(PaddedString(100, "utf8"),
    NONE="_",
    ARMOR="armor",
    ARTILLERY="artillery",
    MELEE="melee",
    RANGED="ranged",
    CASTER="caster"
  ),
  "level" / Int32ul,
  "level_max" / Int32ul,
  "unknown_int_1" / Int32ul, # ?
  "art" / PaddedString(100, "utf8")
)

ObserverPlayerBuilding = Struct(
  "id" / FlippedByteId,
  Padding(100), # name
  "progress_percent" / Int32ul,
  "upgrade_progress_percent" / Int32ul,
  "art" / PaddedString(100, "utf8")
)

ObserverPlayerHeroItem = Struct(
  "id" / FlippedByteId,
  Padding(100), # name
  "slot" / Int32ul,
  "charges" / Int32ul,
  "art" / PaddedString(100, "utf8")
)

ObserverPlayerHeroAbility = Struct(
  "id" / FlippedByteId,
  Padding(36), # name
  "cooldown_time" / Float32l, # in seconds
  "cooldown" / Float32l, # in seconds
  "level" / Int32ul,
  "art" / PaddedString(100, "utf8"),
  "is_hero_ability" / BooleanAdapter(Byte),
  "damage_dealt" / Int32ul,
  "damage_healed" / Int32ul
)

ObserverPlayerHero = Struct(
  "id" / FlippedByteId,
  "class" / PaddedString(100, "utf8"),
  "art" / PaddedString(100, "utf8"),
  "level" / Int32ul,
  "experience" / Int32ul,
  "experience_max" / Int32ul,
  "hitpoints" / Int32ul,
  "hitpoints_max" / Int32ul,
  "mana" / Int32ul,
  "mana_max" / Int32ul,
  "damage_dealt" / Int32ul,
  "damage_received" / Int32ul,
  "damage_self" / Int32ul,
  "index" / Int32ul,
  "damage_healed" / Int32ul,
  "deaths_count" / Int32ul,
  "kills_count" / Int32ul,
  "kills_self" / Int32ul,
  "kills_heroes" / Int32ul,
  "kills_buildings" / Int32ul,
  "time_alive" / Int32ul, # in ms
  "abilities_count" / Int32ul,
  "abilities" / Padded(24 * ObserverPlayerHeroAbility.sizeof(), Array(this.abilities_count, ObserverPlayerHeroAbility)),
  "inventory_count" / Int32ul,
  "inventory" / Padded(6 * ObserverPlayerHeroItem.sizeof(), Array(this.inventory_count, ObserverPlayerHeroItem))
)

ObserverPlayer = Struct(
  "name" / Utf8FallbackAdapter(FixedSized(36, NullStripped(GreedyBytes))), # fallback to None if name fails
                                                                           # to be decoded
  "race_preference" / Enum(Byte,
    HUMAN=0x01,
    ORC=0x02,
    NIGHTELF=0x04,
    UNDEAD=0x08,
    DEMON=0x10,
    RANDOM=0x20,
    SELECTABLE=0x40
  ),
  "race" / Enum(Byte,
    UNKNOWN=0,
    HUMAN=1,
    ORC=2,
    UNDEAD=3,
    NIGHTELF=4,
    DEMON=5,
    LAST=6,
    OTHER=7,
    CREEP=8,
    COMMONER=9,
    CRITTER=10,
    NAGA=11
  ),
  "id" / Byte,
  "team_index" / Byte,
  "team_color" / Byte,
  "type" / Enum(Byte, EMPTY=0, PLAYER=1, COMPUTER=2, NEUTRAL=3, OBSERVER=4, NONE=5, OTHER=6),
  "handicap" / Int32ul,
  "game_result" / Enum(Byte, VICTORY=0, DEFEAT=1, TIE=2, IN_PROGRESS=3),
  "slot_state" / Enum(Byte, EMPTY=0, PLAYING=1, LEFT=2),
  "ai_difficulty" / Enum(Byte, EASY=0, NORMAL=1, INSANE=2),
  "apm" / Int32ul,
  "apm_realtime" / Int32ul,
  "gold" / Int32ul,
  "gold_mined" / Int32ul,
  "gold_taxed" / Int32ul,
  "gold_tax" / Int32ul,
  "lumber" / Int32ul,
  "lumber_harvested" / Int32ul,
  "lumber_taxed" / Int32ul,
  "lumber_tax" / Int32ul,
  "food_max" / Int32ul,
  "food" / Int32ul,
  # paddings are done on every array, usually with 999 maximums: every struct must be of fixed size
  "heroes_count" / Int32ul,
  "heroes" / Padded(999 * ObserverPlayerHero.sizeof(), Array(this.heroes_count, ObserverPlayerHero)),
  "buildings_on_map_count" / Int32ul,
  "buildings_on_map" / Padded(999 * ObserverPlayerBuilding.sizeof(), Array(this.buildings_on_map_count, ObserverPlayerBuilding)),
  "upgrades_completed_count" / Int32ul,
  "upgrades_completed" / Padded(999 * ObserverPlayerUpgrade.sizeof(), Array(this.upgrades_completed_count, ObserverPlayerUpgrade)),
  "units_on_map_count" / Int32ul,
  "units_on_map" / Padded(999 * ObserverPlayerUnit.sizeof(), Array(this.units_on_map_count, ObserverPlayerUnit)), # including heroes and corpses
  "researches_in_progress_count" / Int32ul,
  "researches_in_progress" / Padded(999 * ObserverPlayerResearch.sizeof(), Array(this.researches_in_progress_count, ObserverPlayerResearch)), # including unit training
  Padding(135868), # item history and count, dismissed for now
  Padding(40) # ? upkeep times, dismissed for now
)

ObserverGame = Struct(
  "refresh_rate" / Int32ul,
  "is_in_game" / BooleanAdapter(Byte),
  "game_time" / Int32ul, # in ms
  "players_count" / Byte,
  "game_name" / PaddedString(256, "utf8"),
  "map_name" / PaddedString(256, "utf8")
)

ObserverFile = Struct(
  "version" / Int32ul,
  "game" / ObserverGame,
  "players" / Array(28, ObserverPlayer),
  Padding(1547451) # shops on map, dismissed for now
)
