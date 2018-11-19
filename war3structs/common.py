from construct import *

Integer = Int32sl
Short = Int16sl
Float = Float32l
String = CString("utf8")

class ByteStringAdapter(Adapter):
  def _decode(self, obj, context, path):
    return bytes(obj)

  def _encode(self, obj, context, path):
    return list(obj)

ByteId = ByteStringAdapter(Byte[4])

class BooleanAdapter(Adapter):
  def __init__(self, subcon, falseval=0, trueval=1):
    super(BooleanAdapter, self).__init__(subcon)
    self.falseval = falseval if isinstance(falseval, list) else [falseval]
    self.trueval = trueval if isinstance(trueval, list) else [trueval]

  def _decode(self, obj, context, path):
    return obj not in self.falseval

  def _encode(self, obj, context, path):
    return self.trueval[0] if obj else self.falseval[0]

IntegerBoolean = BooleanAdapter(Integer)

Color = Struct(
  "r" / Byte,
  "g" / Byte,
  "b" / Byte,
  "a" / Byte
)
