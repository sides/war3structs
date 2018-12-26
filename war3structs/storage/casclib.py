# Python CascLib wrapper
#
# Links
#   CascLib API (CascLib.h)
#   - https://github.com/ladislav-zezula/CascLib
#

import os

from enum import IntFlag
from ctypes import (
  CDLL,
  Structure,
  POINTER,
  c_byte,
  c_char,
  c_char_p,
  c_void_p,
  c_uint,
  c_bool
)

chandle = CDLL(os.path.dirname(__file__) + '/CascLib')

class CascError(Exception):
  def __init__(self, message, error, code):
    self.message = message
    self.error = error
    self.code = code

  def __repr__(self):
    return self.message

  def __str__(self):
    return self.message

# Wrapper around CascLib to check for errors
class CascWrapper(type):
  def __getattr__(self, attr):
    if (attr.startswith("Try")):
      funcname = attr[3:]
      return lambda *args: self._tryexec(funcname, *args)

    return lambda *args: self._exec(attr, *args)

  def _tryexec(self, funcname, *args):
    try:
      return self._exec(funcname, *args)
    except:
      return False

  def _exec(self, funcname, *args):
    # debug
    #print(funcname, args)

    # Call the function
    func = getattr(chandle, funcname)
    ret = func(*args)

    # debug
    #print(ret)

    # Handle errors
    code = chandle.GetLastError()
    if ret == 0 and code != 0:
      error = CascErrors.get(code, 'Error %s' % code)
      message = '%s\nCall: %s %s -> %s' % (error, funcname, args, ret)
      raise CascError(message, error, code)

    return ret

# Allows for Casc.<function>()
class Casc(metaclass=CascWrapper):
  pass

CascErrors = {
  2: "ERROR_FILE_NOT_FOUND"
}

class CascFile(Structure):
  _fields_ = [
    ('szFileName', c_char * 1024),
    ('szPlainName', c_char_p),
    ('FileKey', c_byte),
    ('dwLocaleFlags', c_uint),
    ('dwFileDataId', c_uint),
    ('dwFileSize', c_uint),
    ('dwOpenFlags', c_uint)
  ]

  @property
  def filename(self):
    return self.szFileName.decode('utf-8')

  @property
  def basename(self):
    return os.path.basename(self.filename)

  @property
  def dirname(self):
    return os.path.dirname(self.filename)

  def __repr__(self):
    return self.filename

  def __str__(self):
    return self.filename

  def __hash__(self):
    return hash(self.szFileName)

  def __eq__(self, other):
    return self.szFileName == other.szFileName

  def __ne__(self, other):
    return self.szFileName != other.szFileName

# Note: Only add apis that are used in cascstorage
chandle.CascOpenStorage.restype = c_bool
chandle.CascOpenStorage.argtypes = [c_char_p, c_uint, POINTER(c_void_p)]

chandle.CascCloseStorage.restype = c_bool
chandle.CascCloseStorage.argtypes = [c_void_p]

chandle.CascOpenFile.restype = c_bool
chandle.CascOpenFile.argtypes = [c_void_p, c_char_p, c_uint, c_uint, POINTER(c_void_p)]

chandle.CascGetFileSize.restype = c_uint
chandle.CascGetFileSize.argtypes = [c_void_p, POINTER(c_uint)]

chandle.CascReadFile.restype = c_bool
chandle.CascReadFile.argtypes = [c_void_p, c_void_p, c_uint, POINTER(c_uint)]

chandle.CascCloseFile.restype = c_bool
chandle.CascCloseFile.argtypes = [c_void_p]

chandle.CascFindFirstFile.restype = c_void_p
chandle.CascFindFirstFile.argtypes = [c_void_p, c_char_p, POINTER(CascFile), c_char_p]

chandle.CascFindNextFile.restype = c_bool
chandle.CascFindNextFile.argtypes = [c_void_p, POINTER(CascFile)]

chandle.CascFindClose.restype = c_bool
chandle.CascFindClose.argtypes = [c_void_p]
