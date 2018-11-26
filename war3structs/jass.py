import re
import io

from lark import Lark, Tree as BaseTree, Token as BaseToken

"""
  Formats: j

  This is a plain text parser for creating an AST out of JASS code, NOT
  a binary format parser. It is based on Lark instead of construct. The
  grammar is in Lark's EBNF-like syntax and is pretty self-explanatory.
  The parser is able to do some extra things from what Lark can do,
  including parsing comments and reconstructing a script, providing
  similar features to our other constructs.
"""

grammar = """
  //-------------------------------------------------------------------
  // Terminals
  //-------------------------------------------------------------------

  // Keywords
  CODE        : "code"
  HANDLE      : "handle"
  INTEGER     : "integer"
  REAL        : "real"
  BOOLEAN     : "boolean"
  STRING      : "string"
  ARRAY       : "array"
  GLOBALS     : "globals"
  ENDGLOBALS  : "endglobals"
  CONSTANT    : "constant"
  NATIVE      : "native"
  EXTENDS     : "extends"
  KTYPE       : "type"
  FUNCTION    : "function"
  ENDFUNCTION : "endfunction"
  TAKES       : "takes"
  RETURNS     : "returns"
  NOTHING     : "nothing"
  LOCAL       : "local"
  RETURN      : "return"
  SET         : "set"
  CALL        : "call"
  LOOP        : "loop"
  ENDLOOP     : "endloop"
  EXITWHEN    : "exitwhen"
  IF          : "if"
  THEN        : "then"
  ELSE        : "else"
  ELSEIF      : "elseif"
  ENDIF       : "endif"
  DEBUG       : "debug"

  // Identifier
  ID      : ("a".."z"|"A".."Z") ("a".."z"|"A".."Z"|"0".."9"|"_")*
  TYPE    : ID | CODE | HANDLE | INTEGER | REAL | BOOLEAN | STRING

  // Constants
  INT_CONST_DEC.5 : "0" | "1".."9" ("0".."9")*
  INT_CONST_OCT.6 : "0" ("0".."7")+
  INT_CONST_HEX.7 : "$" ("0".."9"|"a".."f"|"A".."F")+ | "0" ("x"|"X") ("0".."9"|"a".."f"|"A".."F")+
  REAL_CONST.8    : ("0".."9")+ "." ("0".."9")* | "." ("0".."9")+
  BOOL_CONST.3    : "true" | "false"
  NULL_CONST.1    : "null"

  // Literals
  STRING_LITERAL.2 : "\\"" ("\\\\\\""|"\\\\\\\\"|/[^"]/)* "\\""
  INT_LITERAL.4    : "'" /[^']*/ "'"

  // Operators
  PLUS    : "+"
  MINUS   : "-"
  TIMES   : "*"
  DIVIDE  : "/"
  OR      : "or"
  AND     : "and"
  NOT     : "not"
  EQ      : "=="
  NE      : "!="
  LT      : "<"
  GT      : ">"
  LE      : "<="
  GE      : ">="

  // Assignment
  EQUALS : "="

  // Delimiters
  LPARENS  : "("
  RPARENS  : ")"
  LBRACKET : "["
  RBRACKET : "]"
  COMMA    : ","


  //-------------------------------------------------------------------
  // Rules
  //-------------------------------------------------------------------

  start : ((type_declr | globals | native_func_declr) NEWLINE)* (func NEWLINE)*


  // Declarations

  type_declr        : KTYPE ID EXTENDS (HANDLE | ID)

  globals           : GLOBALS NEWLINE global_var_declr* ENDGLOBALS

  global_var_declr  : (CONSTANT TYPE ID EQUALS expr NEWLINE | _var_declr NEWLINE)

  native_func_declr : CONSTANT? NATIVE func_declr

  func_declr        : ID TAKES (NOTHING | TYPE ID (COMMA TYPE ID)*) RETURNS (NOTHING | TYPE)

  local_var_declr   : LOCAL _var_declr

  _var_declr        : TYPE ID (EQUALS expr)? | TYPE ARRAY ID


  // Functions

  func   : CONSTANT? FUNCTION func_declr NEWLINE locals statements ENDFUNCTION

  locals : (local_var_declr NEWLINE)*

  args   : expr (COMMA expr)*


  // Statements

  statements      : (_statement NEWLINE)*

  loop_statements : (_statement NEWLINE | exitwhen NEWLINE)* -> statements

  _statement      : set | call | ifthenelse | loop | return | debug

  set             : SET ID EQUALS expr | SET ID LBRACKET expr RBRACKET EQUALS expr

  call            : CALL func_call

  ifthenelse      : IF expr THEN NEWLINE statements (ELSEIF expr THEN NEWLINE statements)* (ELSE NEWLINE statements)? ENDIF

  loop            : LOOP NEWLINE loop_statements ENDLOOP

  exitwhen        : EXITWHEN expr

  return          : RETURN expr?

  debug           : DEBUG (set | call | ifthenelse | loop)


  // Expressions

  expr           : binary_op | unary_op | func_call | array_ref | func_ref | ID | _const | parens

  binary_op      : expr (PLUS | MINUS | TIMES | DIVIDE | EQ | NE | LT | GT | LE | GE | AND | OR) expr

  unary_op       : (PLUS | MINUS | NOT) expr

  func_call      : ID LPARENS args? RPARENS

  array_ref      : ID LBRACKET expr RBRACKET

  func_ref       : FUNCTION ID

  _const         : REAL_CONST | INT_CONST_HEX | INT_CONST_OCT | INT_CONST_DEC | INT_LITERAL | BOOL_CONST | STRING_LITERAL | NULL_CONST

  parens         : LPARENS expr RPARENS


  NEWLINE    : /([\\r]?[\\n])+/
  WHITESPACE : /[ \\t\\f\\r\\n]+/
  COMMENT    : /\\/\\/[^\\n]*/

  %ignore COMMENT
  %ignore WHITESPACE
"""

class Tree(BaseTree):
  pass

class Token(BaseToken):
  pass

class JassParser():
  _build_space_before = [
    'TAKES', 'RETURNS', 'EXTENDS',
    'THEN',
    'AND', 'OR'
  ]

  _build_space_after = [
    'CONSTANT', 'NATIVE', 'KTYPE', 'TYPE', 'ARRAY', 'EXTENDS',
    'FUNCTION', 'TAKES', 'RETURNS',
    'SET', 'CALL', 'LOCAL', 'EXITWHEN', 'DEBUG',
    'IF', 'ELSEIF', 'ELSE', 'RETURN',
    'AND', 'OR', 'NOT'
  ]

  _lark = None

  def _get_lark():
    if JassParser._lark is None:
      JassParser._lark = Lark(grammar, parser="lalr", tree_class=Tree)

    return JassParser._lark

  def parse(text):
    """Get the AST of JASS code"""

    return JassParser._get_lark().parse(text)

  def parse_comments(text):
    """Get comments present in the text by their line numbers"""

    lineno = 1
    comments = {}

    for line in text.splitlines():
      comment_index = line.find('//')
      quote_index = line.find('"')

      if quote_index < comment_index:
        # Remove the quote in case the // is inside it
        line = re.sub(r'"(\\"|\\\\|[^"])*"', '', line)
        comment_index = line.find('//')

      if comment_index != -1:
        comments[lineno] = line[comment_index:]

      lineno += 1

    return comments

  def build(ast):
    """Build a JASS script from an AST"""

    stream = io.StringIO('')

    with stream:
      gen = ast.scan_values(lambda p: True)
      cur = next(gen, None)

      while cur is not None:
        nxt = next(gen, None)

        if cur.type == 'NEWLINE':
          val = '\n'
        else:
          if cur.type in JassParser._build_space_before:
            val = ' '
          else:
            val = ''
          val += cur.value
          if (cur.type in JassParser._build_space_after and
            not nxt is None and not nxt.type == 'NEWLINE'):
            val += ' '

        stream.write(val)
        cur = nxt

      return stream.getvalue()
