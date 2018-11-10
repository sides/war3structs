from construct import *
from .common import *

"""
  Formats: wct
  Version: 1

  The custom triggers file contains JASS code triggers in the map.
"""

CustomTrigger = Struct(
  "code_size" / Integer, # including null terminated char
  "code" / String # is of the length above
)

CustomTriggersFile = Struct(
  "version" / Integer,
  "script_header_comment" / String,
  "script_header_trigger" / CustomTrigger,
  "triggers_count" / Integer,
  "triggers" / Array(this.triggers_count, CustomTrigger)
)
