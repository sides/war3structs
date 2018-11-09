from construct import *
from structs.common import *

"""
  Formats: w3x

  The map file is the structure of maps themselves. They are just MPQs
  with a special header and footer.
"""

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
