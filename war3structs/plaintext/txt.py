import io
import configparser

"""
  Formats: txt

  This is a plain text parser for the INI-like format present in the
  Warcraft III installation files.
"""

class TxtParser():
  def parse(text):
    """Get a config object from text"""

    config = configparser.ConfigParser(
      delimiters=('='),
      # We will interpret the options starting with _ as comments
      # to speed up parsing. If these options are ever meaningful
      # that can change.
      comment_prefixes=('//', '_'),
      strict=False
    )
    config.optionxform = str

    config.read_string(text)

    return config

  def build(config):
    """Build txt from a config object"""

    stream = io.StringIO('')
    config.write(stream)

    return stream.read()
