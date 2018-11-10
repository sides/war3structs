from construct import *
from .common import *

"""
  Formats: imp
  Version: 1

  The imports file contains the import definitions for the map.
"""

Import = Struct(
  "is_custom_path" / Byte, # 5 or 8 for no, 10 or 13 for yes
  "path" / String
)

ImportsFile = Struct(
  "version" / Integer,
  "imports_count" / Integer,
  "imports" / Array(this.imports_count, Import)
)
