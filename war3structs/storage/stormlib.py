# Python StormLib wrapper
#
# Originally by Vjeux <vjeuxx@gmail.com> (WTFPL)
# https://github.com/vjeux/pyStormLib
#
# This is an updated version (with write) for the war3archiver
# https://github.com/warlockbrawl/war3archiver
#
# Links
#   StormLib API
#   - http://www.zezula.net/en/mpq/stormlib.html
#

import os

from enum import IntFlag
from ctypes import (
  CDLL,
  Structure,
  POINTER,
  c_char,
  c_char_p,
  c_void_p,
  c_uint,
  c_uint64,
  c_int64,
  c_bool
)

shandle = CDLL(os.path.dirname(__file__) + '/storm')

class StormError(Exception):
  def __init__(self, message, error, code):
    self.message = message
    self.error = error
    self.code = code

  def __repr__(self):
    return self.message

  def __str__(self):
    return self.message

# Wrapper around storm to check for errors
class StormWrapper(type):
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
    func = getattr(shandle, funcname)
    ret = func(*args)

    # debug
    #print(ret)

    # Handle errors
    code = shandle.GetLastError()
    if ret == 0 and code not in (0, 106, 107): # "No more files" and "End of file" are not real errors
      error = StormErrors.get(code, 'Error %s' % code)
      message = '%s\nCall: %s %s -> %s' % (error, funcname, args, ret)
      raise StormError(message, error, code)

    return ret

# Allows for Storm.<function>()
class Storm(metaclass=StormWrapper):
  pass

StormErrors = {
  10000: "ERROR_AVI_FILE Not an MPQ file, but an AVI file.",
  10001: "ERROR_UNKNOWN_FILE_KEY Returned by SFileReadFile when can't find file key",
  10002: "ERROR_CHECKSUM_ERROR Returned by SFileReadFile when sector CRC doesn't match",
  10003: "ERROR_INTERNAL_FILE The given operation is not allowed on internal file",
  10004: "ERROR_BASE_FILE_MISSING The file is present as incremental patch file, but base file is missing",
  10005: "ERROR_MARKED_FOR_DELETE The file was marked as \"deleted\" in the MPQ",
  10006: "ERROR_FILE_INCOMPLETE The required file part is missing",
  10007: "ERROR_UNKNOWN_FILE_NAMES A name of at least one file is unknown",
  10008: "ERROR_CANT_FIND_PATCH_PREFIX StormLib was unable to find patch prefix for the patches",

  5:    "ERROR_ACCESS_DENIED",
  6:    "ERROR_INVALID_HANDLE",
  11:   "ERROR_BAD_FORMAT",
  32:   "ERROR_ACCESS_DENIED",
  112:  "ERROR_DISK_FULL",
  183:  "ERROR_ALREADY_EXISTS",

  1000: "ERROR_BAD_FORMAT",
  1001: "ERROR_NO_MORE_FILES",
  1002: "ERROR_HANDLE_EOF",
  1003: "ERROR_CAN_NOT_COMPLETE",
  1004: "ERROR_FILE_CORRUPT"
}

class StormOpenArchiveFlag(IntFlag):
  STREAM_FLAG_READ_ONLY     = 0x00000100
  STREAM_FLAG_WRITE_SHARE   = 0x00000200
  STREAM_FLAG_USE_BITMAP    = 0x00000400
  MPQ_OPEN_NO_LISTFILE      = 0x00010000
  MPQ_OPEN_NO_ATTRIBUTES    = 0x00020000
  MPQ_OPEN_NO_HEADER_SEARCH = 0x00040000
  MPQ_OPEN_FORCE_MPQ_V1     = 0x00080000
  MPQ_OPEN_CHECK_SECTOR_CRC = 0x00100000

class StormCreateArchiveFlag(IntFlag):
  MPQ_CREATE_LISTFILE   = 0x00100000
  MPQ_CREATE_ATTRIBUTES = 0x00200000
  MPQ_CREATE_SIGNATURE  = 0x00400000
  MPQ_CREATE_ARCHIVE_V1 = 0x00000000
  MPQ_CREATE_ARCHIVE_V2 = 0x01000000
  MPQ_CREATE_ARCHIVE_V3 = 0x02000000
  MPQ_CREATE_ARCHIVE_V4 = 0x03000000

class StormAddFileFlag(IntFlag):
  MPQ_FILE_IMPLODE         = 0x00000100
  MPQ_FILE_COMPRESS        = 0x00000200
  MPQ_FILE_ENCRYPTED       = 0x00010000
  MPQ_FILE_FIX_KEY         = 0x00020000
  MPQ_FILE_DELETE_MARKER   = 0x02000000
  MPQ_FILE_SECTOR_CRC      = 0x04000000
  MPQ_FILE_SINGLE_UNIT     = 0x01000000
  MPQ_FILE_REPLACEEXISTING = 0x80000000

class StormCompressFileFlag(IntFlag):
  MPQ_COMPRESSION_HUFFMANN     = 0x01
  MPQ_COMPRESSION_ZLIB         = 0x02
  MPQ_COMPRESSION_PKWARE       = 0x08
  MPQ_COMPRESSION_BZIP2        = 0x10
  MPQ_COMPRESSION_SPARSE       = 0x20
  MPQ_COMPRESSION_ADPCM_MONO   = 0x40
  MPQ_COMPRESSION_ADPCM_STEREO = 0x80
  MPQ_COMPRESSION_LZMA         = 0x12

class StormFile(Structure):
  _fields_ = [
    ('cFileName', c_char * 1024),
    ('szPlainName', c_char_p),
    ('dwHashIndex', c_uint),
    ('dwBlockIndex', c_uint),
    ('dwFileSize', c_uint),
    ('dwFileFlags', c_uint),
    ('dwCompSize', c_uint),
    ('dwFileTimeLo', c_uint),
    ('dwFileTimeHi', c_uint),
    ('lcLocale', c_uint)
  ]

  @property
  def filename(self):
    return self.cFileName.decode('utf-8')

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
    return hash(self.cFileName)

  def __eq__(self, other):
    return self.cFileName == other.cFileName

  def __ne__(self, other):
    return self.cFileName != other.cFileName

# Note: Only add apis that are used in stormmpq
shandle.SFileOpenArchive.restype = c_bool
shandle.SFileOpenArchive.argtypes = [c_char_p, c_uint, c_uint, POINTER(c_void_p)]

shandle.SFileCreateArchive.restype = c_bool
shandle.SFileCreateArchive.argtypes = [c_char_p, c_uint, c_uint, POINTER(c_void_p)]

shandle.SFileCloseArchive.restype = c_bool
shandle.SFileCloseArchive.argtypes = [c_void_p]

shandle.SFileGetMaxFileCount.restype = c_uint
shandle.SFileGetMaxFileCount.argtypes = [c_void_p]

shandle.SFileSetMaxFileCount.restype = c_bool
shandle.SFileSetMaxFileCount.argtypes = [c_void_p, c_uint]

shandle.SFileCompactArchive.restype = c_bool
shandle.SFileCompactArchive.argtypes = [c_void_p, c_char_p, c_bool]

shandle.SFileOpenPatchArchive.restype = c_bool
shandle.SFileOpenPatchArchive.argtypes = [c_void_p, c_char_p, c_char_p, c_uint]

shandle.SFileOpenFileEx.restype = c_bool
shandle.SFileOpenFileEx.argtypes = [c_void_p, c_char_p, c_uint, POINTER(c_void_p)]

shandle.SFileGetFileSize.restype = c_uint
shandle.SFileGetFileSize.argtypes = [c_void_p, POINTER(c_uint)]

shandle.SFileReadFile.restype = c_bool
shandle.SFileReadFile.argtypes = [c_void_p, c_void_p, c_uint, POINTER(c_uint), POINTER(c_void_p)]

shandle.SFileCloseFile.restype = c_bool
shandle.SFileCloseFile.argtypes = [c_void_p]

shandle.SFileHasFile.restype = c_bool
shandle.SFileHasFile.argtypes = [c_void_p, c_char_p]

shandle.SFileExtractFile.restype = c_bool
shandle.SFileExtractFile.argtypes = [c_void_p, c_char_p, c_char_p, c_uint]

shandle.SFileFindFirstFile.restype = c_void_p
shandle.SFileFindFirstFile.argtypes = [c_void_p, c_char_p, POINTER(StormFile), c_char_p]

shandle.SFileFindNextFile.restype = c_bool
shandle.SFileFindNextFile.argtypes = [c_void_p, POINTER(StormFile)]

shandle.SFileFindClose.restype = c_bool
shandle.SFileFindClose.argtypes = [c_void_p]

shandle.SFileCreateFile.restype = c_bool
shandle.SFileCreateFile.argtypes = [c_void_p, c_char_p, c_uint64, c_uint, c_uint, c_uint, POINTER(c_void_p)]

shandle.SFileWriteFile.restype = c_bool
shandle.SFileWriteFile.argtypes = [c_void_p, POINTER(c_char_p), c_uint, c_uint]

shandle.SFileFinishFile.restype = c_bool
shandle.SFileFinishFile.argtypes = [c_void_p]

shandle.SFileAddFileEx.restype = c_bool
shandle.SFileAddFileEx.argtypes = [c_void_p, c_char_p, c_char_p, c_uint, c_uint, c_uint]

shandle.SFileRemoveFile.restype = c_bool
shandle.SFileRemoveFile.argtypes = [c_void_p, c_char_p, c_uint]

shandle.SFileRenameFile.restype = c_bool
shandle.SFileRenameFile.argtypes = [c_void_p, c_char_p, c_char_p]
