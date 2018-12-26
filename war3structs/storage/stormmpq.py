# StormLib MPQ implementation
#
# Originally by Vjeux <vjeuxx@gmail.com> (WTFPL)
# https://github.com/vjeux/pyStormLib
#
# This is an updated version (with write) for the war3archiver
# https://github.com/warlockbrawl/war3archiver
#

import os
import glob
import sys

from ctypes import (
  byref,
  c_void_p,
  c_char_p,
  c_uint,
  c_uint64,
  create_string_buffer
)
from .stormlib import (
  Storm,
  StormError,
  StormOpenArchiveFlag,
  StormCreateArchiveFlag,
  StormAddFileFlag,
  StormCompressFileFlag,
  StormFile
)

class MPQFile(StormFile):
  def __init__(self, mpq):
    self.mpq = mpq

  def contents(self):
    return self.mpq.read(self.filename)

  def extract(self, target=None):
    return self.mpq.extract(self.filename, target)

  def rename(self, newpath):
    return self.mpq.rename(self.filename, newpath)

  def remove(self):
    return self.mpq.remove(self.filename)

class MPQ():
  def __init__(self, filename, readonly=True):
    """Open or create an archive."""

    self.mpq_h = c_void_p()

    if os.path.exists(filename):
      flags = 0
      if readonly:
        flags |= StormOpenArchiveFlag.STREAM_FLAG_READ_ONLY

      Storm.SFileOpenArchive(filename.encode('utf-8'), 0, flags, byref(self.mpq_h))
    else:
      Storm.SFileCreateArchive(filename.encode('utf-8'), 0, 256, byref(self.mpq_h))

  def close(self):
    """Close the archive."""

    Storm.SFileCloseArchive(self.mpq_h)
    self.mpq_h = None

  def compact(self):
    """Compact the archive.

    Requires a complete listfile.
    I'm not entirely sure what this actually does.
    """
    Storm.SFileCompactArchive(self.mpq_h, None, 0)

  def getsize(self):
    """Get the hashtable size of the archive."""

    return Storm.SFileGetMaxFileCount(self.mpq_h)

  def setsize(self, size):
    """Set the hashtable size of the archive.

    Requires a complete listfile and typically errors when decreasing
    size. Use with care!
    """
    size = min(max(size, 4), 524288)

    Storm.SFileSetMaxFileCount(self.mpq_h, size)

  def find(self, mask='*'):
    """List all files matching a mask."""

    found = set([])

    # Initial find
    file = MPQFile(self)
    find_h = Storm.SFileFindFirstFile(self.mpq_h, mask.encode('utf-8'), byref(file), None)
    if not find_h or not str(file):
      return

    yield file
    found.add(file)

    # Go through the results
    file = MPQFile(self)
    while Storm.TrySFileFindNextFile(find_h, byref(file)):
      if not str(file) or file in found:
        break

      yield file
      found.add(file)
      file = MPQFile(self)

    # Close the handle
    Storm.SFileFindClose(find_h)

  def has(self, path):
    """Does the archive have the file?"""

    # Handle argument
    if isinstance(path, StormFile):
      path = path.filename

    return Storm.TrySFileHasFile(self.mpq_h, path.encode('utf-8'))

  def read(self, path):
    """Return a file's contents."""

    # Handle argument
    if isinstance(path, StormFile):
      path = path.filename

    # Open the file
    file_h = c_void_p()
    Storm.SFileOpenFileEx(self.mpq_h, path.encode('utf-8'), 0, byref(file_h))

    # Get the size
    high = c_uint()
    low = Storm.SFileGetFileSize(file_h, byref(high))
    size = high.value * pow(2, 32) + low

    # Read the file
    data = create_string_buffer(size)
    read = c_uint()
    Storm.SFileReadFile(file_h, byref(data), size, byref(read), None)

    # Close and return
    Storm.SFileCloseFile(file_h)
    return data.raw

  def write(self, path, data, compress=True, replace=False):
    """Write data to a new file."""

    size = len(data)
    data = c_char_p(data)
    file_h = c_void_p()

    flags = 0
    if compress:
      flags |= StormAddFileFlag.MPQ_FILE_COMPRESS
    if replace:
      flags |= StormAddFileFlag.MPQ_FILE_REPLACEEXISTING

    Storm.SFileCreateFile(self.mpq_h, path.encode('utf-8'), 0, size, 0, flags, byref(file_h))
    Storm.SFileWriteFile(file_h, byref(data), size, 0)
    Storm.SFileFinishFile(file_h)

  def rename(self, path, newpath):
    """Rename a file."""

    if isinstance(path, StormFile):
      path = path.filename

    Storm.SFileRenameFile(self.mpq_h, path.encode('utf-8'), newpath.encode('utf-8'))

  def remove(self, path):
    """Remove a file from the archive."""

    if isinstance(path, StormFile):
      path = path.filename

    Storm.SFileRemoveFile(self.mpq_h, path.encode('utf-8'), 0)

  def extract(self, mpq_path, local_path=None):
    """Extract a file from the archive."""

    # Handle arguments
    if isinstance(mpq_path, StormFile):
      mpq_path = mpq_path.filename

    if local_path is None:
      local_path = mpq_path.replace('\\', '/')

    # Create the directories
    try:
      os.makedirs(os.path.dirname(local_path))
    except FileExistsError:
      pass

    # Extract
    Storm.SFileExtractFile(self.mpq_h, mpq_path.encode('utf-8'), local_path.encode('utf-8'), 0)

  def add(self, local_path, mpq_path=None, compress=True, replace=False):
    """Add a local file to the archive"""

    if mpq_path is None:
      mpq_path = os.path.basename(local_path)
    elif isinstance(mpq_path, StormFile):
      mpq_path = mpq_path.filename

    flags = 0
    if compress:
      flags |= StormAddFileFlag.MPQ_FILE_COMPRESS
    if replace:
      flags |= StormAddFileFlag.MPQ_FILE_REPLACEEXISTING

    Storm.SFileAddFileEx(self.mpq_h, local_path.encode('utf-8'), mpq_path.encode('utf-8'), flags, 0, 0)

  def patch(self, path, prefix=''):
    """Add MPQ as patches"""

    # Handle arguments
    path_list = sorted(glob.glob(path)) if isinstance(path, str) else path

    # Add the patches
    for path in path_list:
      Storm.SFileOpenPatchArchive(self.mpq_h, path.encode('utf-8'), prefix.encode('utf-8'), 0)
