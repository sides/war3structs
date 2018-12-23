from construct import *
from .common import *

"""
  Formats: War3StatsObserverSharedMemory
  Version: 0

  The structure of the memory mapped observer API file. It can be read
  in-game with the mmap python module.
"""

class FlippedByteStringAdapter(Adapter):
  def _decode(self, obj, context, path):
    return bytes(obj[::-1]).decode('utf-8')

  def _encode(self, obj, context, path):
    return list(obj.encode('utf-8'))[::-1]

FlippedByteId = FlippedByteStringAdapter(Byte[4])

ObserverPlayerResearch = Struct(
  "id" / FlippedByteId,
  "name" / PaddedString(100, "utf8"),
  "progress_percent" / Int32ul,
  "type" / Enum(Byte, UPGRADE=0, UNIT=1)
)

ObserverPlayerUnit = Struct(
  "id" / FlippedByteId,
  "name" / PaddedString(100, "utf8"),
  "owning_player_id" / Int32ul, # maybe?
  "alive_count" / Int32ul,
  "total_count" / Int32ul
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
  "unknown_int_1" / Int32ul # ?
)

ObserverPlayerBuilding = Struct(
  "id" / FlippedByteId,
  "name" / PaddedString(100, "utf8"),
  "progress_percent" / Int32ul,
  "upgrade_progress_percent" / Int32ul
)

ObserverPlayerHeroItem = Struct(
  "id" / FlippedByteId,
  "name" / PaddedString(100, "utf8"),
  "slot" / Int32ul,
  "charges" / Int32ul
)

ObserverPlayerHeroAbility = Struct(
  "id" / FlippedByteId,
  "name" / PaddedString(38, "utf8"),
  "unknown_flag_1" / Byte, # ?
  "unknown_flag_2" / Byte, # ?
  "cooldown" / Float32l, # in seconds
  "level" / Int32ul
)

ObserverPlayerHero = Padded(2060, Struct(
  "id" / FlippedByteId,
  "class" / PaddedString(100, "utf8"),
  "level" / Int32ul,
  "experience" / Int32ul,
  "experience_max" / Int32ul,
  "hitpoints" / Int32ul,
  "hitpoints_max" / Int32ul,
  "mana" / Int32ul,
  "mana_max" / Int32ul,
  "abilities_count" / Int32ul,
  "abilities" / Padded(1248, Array(this.abilities_count, ObserverPlayerHeroAbility)),
  "items_count" / Int32ul,
  "items" / Array(this.items_count, ObserverPlayerHeroItem)
))

ObserverPlayer = Padded(2510604, Struct(
  "name" / PaddedString(36, "utf8"),
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
  # why these are padded when they include counts, I don't know
  "heroes_count" / Int32ul,
  "heroes" / Padded(2057940, Array(this.heroes_count, ObserverPlayerHero)),
  "buildings_on_map_count" / Int32ul,
  "buildings_on_map" / Padded(111888, Array(this.buildings_on_map_count, ObserverPlayerBuilding)),
  "upgrades_completed_count" / Int32ul,
  "upgrades_completed" / Padded(115884, Array(this.upgrades_completed_count, ObserverPlayerUpgrade)),
  "units_on_map_count" / Int32ul,
  "units_on_map" / Padded(115884, Array(this.units_on_map_count, ObserverPlayerUnit)), # including heroes and corpses
  "researches_in_progress_count" / Int32ul,
  "researches_in_progress" / Padded(108891, Array(this.researches_in_progress_count, ObserverPlayerResearch)) # including unit training
))

ObserverGame = Struct(
  "is_in_game" / BooleanAdapter(Byte),
  "game_time" / Int32ul, # in ms
  "players_count" / Byte,
  "game_name" / PaddedString(256, "utf8"),
  "map_name" / PaddedString(256, "utf8")
)

ObserverFile = Struct(
  "version" / Int32ul,
  "refresh_rate" / Int32ul,
  "game" / ObserverGame,
  "players" / Array(this.game.players_count, ObserverPlayer)
)
