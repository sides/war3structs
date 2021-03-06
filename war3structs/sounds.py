from construct import *
from .common import *

"""
  Formats: w3s
  Version: 1

  The sounds file contains the sound definitions in a map.
"""

# strings can be "", integers can be -1 and floats can be 0x4F800000
# for "unset" values (uses default)
Sound = Struct(
  "variable" / String,
  "file_path" / String,
  "eax_effect" / Enum(String,
    UNSET = "",
    DEFAULT = "DefaultEAXON",
    COMBAT = "CombatSoundsEAX",
    DRUM = "KotoDrumsEAX",
    SPELL = "SpellsEAX",
    MISSILE = "MissilesEAX",
    SPEECH = "HeroAcksEAX",
    DOODAD = "DoodadsEAX"
  ),
  "flags" / FlagsEnum(Integer,
    is_looping         = 0x01,
    is_3d              = 0x02,
    stops_out_of_range = 0x04,
    is_music           = 0x08
  ),
  "fade_in_rate" / Integer,
  "fade_out_rate" / Integer,
  "volume" / Integer,
  "pitch" / Float,
  "unknown_field_1" / Float, # ?
  "unknown_field_2" / Integer, # ? (-1 or 8)
  "channel" / Enum(Integer,
    UNSET = -1,
    GENERAL = 0,
    UNIT_SELECTION = 1,
    UNIT_ACKNOWLEDGEMENT = 2,
    UNIT_MOVEMENT = 3,
    UNIT_READY = 4,
    COMBAT = 5,
    ERROR = 6,
    MUSIC = 7,
    USER_INTERFACE = 8,
    LOOPING_MOVEMENT = 9,
    LOOPING_AMBIENT = 10,
    ANIMATIONS = 11,
    CONSTRUCTIONS = 12,
    BIRTH = 13,
    FIRE = 14
  ),
  "distance_min" / Float,
  "distance_max" / Float,
  "distance_cutoff" / Float,
  "unknown_field_3" / Float, # ?
  "unknown_field_4" / Float, # ?
  "unknown_field_5" / Integer, # ? (-1 or 127)
  "unknown_field_6" / Float, # ?
  "unknown_field_7" / Float, # ?
  "unknown_field_8" / Float # ?
)

SoundsFile = Struct(
  "version" / Integer,
  "sounds_count" / Integer,
  "sounds" / Array(this.sounds_count, Sound)
)
