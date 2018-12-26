import os
import glob
import sys

from ctypes import (
  byref,
  c_void_p,
  c_uint,
  create_string_buffer
)
from .casclib import (
  Casc,
  CascError,
  CascFile
)

class CascStoreFile(CascFile):
  def __init__(self, store):
    self.store = store

  def contents(self):
    return self.store.read(self.filename)

  def extract(self, target=None):
    return self.store.extract(self.filename, target)

class CascStore():
  def __init__(self, datapath, listfile=None):
    """Open CASC storage."""

    self.listfile = listfile
    self.store_h = c_void_p()

    if not os.path.exists(datapath):
      raise Exception('Tried to open "%s" but no such directory exists' % datapath)

    Casc.CascOpenStorage(datapath.encode('utf-8'), 0, byref(self.store_h))

  def close(self):
    """Close the store."""

    Casc.CascCloseStorage(self.store_h)
    self.store_h = None

  def find(self, mask='*'):
    """List all files matching a mask."""

    if self.listfile is None:
      raise Exception('Store was not initialized with a listfile, can\'t search')

    found = set([])

    # Initial find
    file = CascStoreFile(self)
    find_h = Casc.CascFindFirstFile(self.store_h, mask.encode('utf-8'), byref(file), self.listfile.encode('utf-8'))
    if not find_h or not str(file):
      return

    yield file
    found.add(file)

    # Go through the results
    file = CascStoreFile(self)
    while Casc.TryCascFindNextFile(find_h, byref(file)):
      if not str(file) or file in found:
        break

      yield file
      found.add(file)
      file = CascStoreFile(self)

    # Close the handle
    Casc.CascFindClose(find_h)

  def read(self, path):
    """Return a file's contents."""

    # Handle argument
    if isinstance(path, CascStoreFile):
      path = path.filename

    # Open the file
    file_h = c_void_p()
    Casc.CascOpenFile(self.store_h, path.encode('utf-8'), 0, 0, byref(file_h))

    # Get the size
    high = c_uint()
    low = Casc.CascGetFileSize(file_h, byref(high))
    size = high.value * pow(2, 32) + low

    # Read the file
    data = create_string_buffer(size)
    read = c_uint()
    Casc.CascReadFile(file_h, byref(data), size, byref(read))

    # Close and return
    Casc.CascCloseFile(file_h)
    return data.raw

  def extract(self, mpq_path, local_path=None):
    """Extract a file from the store."""

    # Handle arguments
    if isinstance(mpq_path, CascStoreFile):
      mpq_path = mpq_path.filename

    if local_path is None:
      local_path = os.path.join('.', mpq_path.replace('\\', '/').replace(':', '_'))

    contents = self.read(mpq_path)

    # Create the directories
    try:
      os.makedirs(os.path.dirname(local_path))
    except FileExistsError:
      pass

    # Write to the file
    with open(local_path, 'wb') as file:
      file.write(contents)
