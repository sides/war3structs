from lark import Transformer, Token

#
# The map of our JASS script is very primitive. It's only concerned
# with symbols, mainly allowing code to read what symbols exist in a
# script rather than their implementation. Statements and expressions
# are only mapped as lists of their tokens. They can, however, easily
# be set to something else by lexing source code, but reading them is
# more or less as unintelligible as reading source code.
#
# NOTE: Token values must always be accessed via their `value` attribute.
#       Their str value is not consistent.
#


class Symbol():
  def __init__(self, id, line, column):
    self.line = line
    self.column = column
    self.id = id


class Function(Symbol):
  def __init__(self, id, takes, returns, is_constant, is_native, line=None, column=None):
    super().__init__(id, line, column)
    self.takes = takes
    self.returns = returns
    self.is_constant = is_constant
    self.is_native = is_native


class Variable(Symbol):
  def __init__(self, id, type, is_array, equals, line=None, column=None):
    super().__init__(id, line, column)
    self.type = type
    self.is_array = is_array
    self.equals = equals


class Type(Symbol):
  def __init__(self, id, extends, line=None, column=None):
    super().__init__(id, line, column)
    self.extends = extends


class GlobalVariable(Variable):
  def __init__(self, id, type, is_array, equals, is_constant, line=None, column=None):
    super().__init__(id, type, is_array, equals, line=line, column=column)
    self.is_constant = is_constant


class FunctionDefinition(Function):
  def __init__(self, id, takes, returns, is_constant, locals, statements, line=None, column=None):
    super().__init__(id, takes, returns, is_constant, is_native=False, line=line, column=column)
    self.locals = locals
    self.statements = statements

  def rename_local(self, old_id, new_id):
    for local in self.locals:
      if local.id == old_id:
        local.id = new_id
      elif not local.equals is None:
        for token in local.equals:
          if token.value == old_id and token.type == 'ID':
            token.value = new_id

    for statement in self.statements:
      for token in statement:
        if token.value == old_id and token.type == 'ID':
          token.value = new_id


class Node():
  """Node class

  Nodes are an "unknown", i.e. statements and expressions, that we just
  unzip into one long list of tokens.
  """
  def __init__(self, children):
    self.tokens = []

    for child in children:
      if isinstance(child, Node):
        self.tokens.extend(child.tokens)
      else:
        self.tokens.append(child)


class JassScript():
  def __init__(self, types, natives, globals, functions):
    self.types = types
    self.natives = natives
    self.globals = globals
    self.functions = functions

  def _rename_type(self, symbol, new_id):
    old_id = str(symbol.id)
    symbol.id = new_id

    for type_ in self.types:
      if type_.extends == old_id:
        type_.extends = new_id

    for native in self.natives:
      for index, takes in enumerate(native.takes):
        if takes[0] == old_id:
          native.takes[index] = (new_id, takes[1])

      if native.returns == old_id:
        native.returns = new_id

    for global_ in self.globals:
      if global_.type == old_id:
        global_.type = new_id

    for function in self.functions:
      for index, takes in enumerate(function.takes):
        if takes[0] == old_id:
          function.takes[index] = (new_id, takes[1])

      if function.returns == old_id:
        function.returns = new_id

      for local in function.locals:
        if local.type == old_id:
          local.type = new_id

  def rename(self, old_id, new_id):
    symbol = self[old_id]

    if type(symbol) == Type:
      self._rename_type(symbol, new_id)
      return

    for native in self.natives:
      if native.id == old_id:
        native.id = new_id

    for global_ in self.globals:
      if global_.id == old_id:
        global_.id = new_id

      if not global_.equals is None:
        for token in global_.equals:
          if token.value == old_id and token.type == 'ID':
            token.value = new_id

    for function in self.functions:
      if function.id == old_id:
        function.id = new_id

      for local in function.locals:
        if not local.equals is None:
          for token in local.equals:
            if token.value == old_id and token.type == 'ID':
              token.value = new_id

      for statement in function.statements:
        for token in statement:
          if token.value == old_id and token.type == 'ID':
            token.value = new_id

  def _replace_in_list(self, attr, old, new):
    symbols = getattr(self, attr)
    for index, symbol in enumerate(symbols):
      if symbol == old:
        if new is None:
          del symbols[index]
        else:
          symbols[index] = new
        return

  def replace(self, old, new):
    t = type(old)

    if not type(new) is t and not new is None:
      raise TypeError()

    if t == Type:
      self._replace_in_list('types', old, new)
    elif t == Function:
      self._replace_in_list('natives', old, new)
    elif t == GlobalVariable:
      self._replace_in_list('globals', old, new)
    elif t == FunctionDefinition:
      self._replace_in_list('functions', old, new)
    else:
      raise TypeError()

  def add(self, symbol):
    t = type(symbol)

    if t == Type:
      self.types.append(symbol)
    elif t == Function:
      self.natives.append(symbol)
    elif t == GlobalVariable:
      self.globals.append(symbol)
    elif t == FunctionDefinition:
      self.functions.append(symbol)
    else:
      raise TypeError()

  def __iter__(self):
    for n in self.types + self.natives + self.globals + self.functions:
      yield n.id

  def __getitem__(self, key):
    for n in self.types + self.natives + self.globals + self.functions:
      if n.id == key:
        return n

    raise IndexError()

  def __setitem__(self, key, value):
    try:
      old = self[key]
      self.replace(old, value)
    except IndexError:
      self.add(value)

  def __delitem__(self, key):
    self.replace(self[key], None)

  def get_conga_line(self):
    """Rebuild the script by generating all of its necessary tokens"""

    # I freely admit this is stupid

    for type_ in self.types:
      yield Token('KTYPE', 'type')
      yield Token('ID', type_.id)
      yield Token('EXTENDS', 'extends')
      yield Token('ID', type_.extends)
      yield Token('NEWLINE', '\n')

    for native in self.natives:
      if native.is_constant:
        yield Token('CONSTANT', 'constant')
      yield Token('NATIVE', 'native')
      yield Token('ID', native.id)
      yield Token('TAKES', 'takes')
      if len(native.takes) > 0:
        for takes in native.takes:
          yield Token('TYPE', takes[0])
          yield Token('ID', takes[1])
      else:
        yield Token('NOTHING', 'nothing')
      yield Token('RETURNS', 'returns')
      if native.returns is None:
        yield Token('NOTHING', 'nothing')
      else:
        yield Token('TYPE', native.returns)
      yield Token('NEWLINE', '\n')

    yield Token('GLOBALS', 'globals')
    yield Token('NEWLINE', '\n')
    for global_ in self.globals:
      if global_.is_constant:
        yield Token('CONSTANT', 'constant')
      yield Token('TYPE', global_.type)
      if global_.is_array:
        yield Token('ARRAY', 'array')
      yield Token('ID', global_.id)
      if not global_.equals is None:
        yield Token('EQUALS', '=')
        for token in global_.equals:
          yield token
      yield Token('NEWLINE', '\n')
    yield Token('ENDGLOBALS', 'endglobals')
    yield Token('NEWLINE', '\n')

    for function in self.functions:
      if function.is_constant:
        yield Token('CONSTANT', 'constant')
      yield Token('FUNCTION', 'function')
      yield Token('ID', function.id)
      yield Token('TAKES', 'takes')
      if len(function.takes) > 0:
        for takes in function.takes:
          yield Token('TYPE', takes[0])
          yield Token('ID', takes[1])
      else:
        yield Token('NOTHING', 'nothing')
      yield Token('RETURNS', 'returns')
      if function.returns is None:
        yield Token('NOTHING', 'nothing')
      else:
        yield Token('TYPE', function.returns)
      yield Token('NEWLINE', '\n')
      for local in function.locals:
        yield Token('LOCAL', 'local')
        yield Token('TYPE', local.type)
        if local.is_array:
          yield Token('ARRAY', 'array')
        yield Token('ID', local.id)
        if not local.equals is None:
          yield Token('EQUALS', '=')
          for token in local.equals:
            yield token
        yield Token('NEWLINE', '\n')
      for statement in function.statements:
        for token in statement:
          yield token
        yield Token('NEWLINE', '\n')
      yield Token('ENDFUNCTION', 'endfunction')
      yield Token('NEWLINE', '\n')


class JassScriptTransformer(Transformer):
  """JassScriptTransformer class

  A transformer that returns an instance of JassScript when parsed
  with.
  """

  def expr(self, children):
    return Node(children)

  def statement(self, children):
    return Node(children)

  def statements(self, children):
    return list(map(lambda n: n.tokens, children[::2]))

  def local_var_declr(self, children):
    num = len(children)
    if num == 3:
      return Variable(children[2], children[1], is_array=False, equals=None,
        line=children[0].line, column=children[0].column)
    elif num == 4:
      return Variable(children[3], children[1], is_array=True, equals=None,
        line=children[0].line, column=children[0].column)
    else:
      equals = children[4].tokens if isinstance(children[4], Node) else [children[4]]
      return Variable(children[2], children[1], is_array=False, equals=equals,
        line=children[0].line, column=children[0].column)

  def locals(self, children):
    return children[::2]

  def func_declr_args(self, children):
    return list(zip(children[::3], children[1::3]))

  def func(self, children):
    ofs = 0 if children[0].type != 'CONSTANT' else 1
    takes = [] if not isinstance(children[3+ofs], list) else children[3+ofs]
    returns = None if children[5+ofs].type == 'NOTHING' else children[5+ofs]
    return FunctionDefinition(children[1+ofs], takes, returns, bool(ofs), locals=children[7+ofs], statements=children[8+ofs],
      line=children[0].line, column=children[0].column)

  def global_var_declr(self, children):
    ofs = 0 if children[0].type != 'CONSTANT' else 1
    num = len(children) - ofs
    if num == 2:
      return GlobalVariable(children[1+ofs], children[0+ofs], is_array=False, equals=None, is_constant=bool(ofs),
        line=children[0].line, column=children[0].column)
    elif num == 3:
      return GlobalVariable(children[2+ofs], children[0+ofs], is_array=True, equals=None, is_constant=bool(ofs),
        line=children[0].line, column=children[0].column)
    else:
      equals_child = children[3+ofs]
      equals = equals_child.tokens if isinstance(equals_child, Node) else [equals_child]
      return GlobalVariable(children[1+ofs], children[0+ofs], is_array=False, equals=equals, is_constant=bool(ofs),
        line=children[0].line, column=children[0].column)

  def globals(self, children):
    return children[2:-1:2]

  def native_func_declr(self, children):
    ofs = 0 if children[0].type != 'CONSTANT' else 1
    takes = [] if not isinstance(children[3+ofs], list) else children[3+ofs]
    returns = None if children[5+ofs].type == 'NOTHING' else children[5+ofs]
    return Function(children[1+ofs], takes, returns, bool(ofs), is_native=True,
      line=children[0].line, column=children[0].column)

  def type_declr(self, children):
    return Type(children[1], children[3],
      line=children[0].line, column=children[0].column)

  def start(self, children):
    types = []
    natives = []
    globals = []
    functions = []

    for symbol in children[::2]:
      t = type(symbol)
      if t == Type:
        types.append(symbol)
      elif t == Function:
        natives.append(symbol)
      elif t == FunctionDefinition:
        functions.append(symbol)
      elif t == list:
        globals.extend(symbol)

    return JassScript(types, natives, globals, functions)
