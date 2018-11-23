from lark import Lark

"""
  Formats: j

  This is a plain text parser for creating an AST out of JASS code, NOT
  a binary format parser. It uses Lark, not construct. The grammar is
  in Lark's EBNF-like syntax, but is pretty self-explanatory.
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

  start : NEWLINE* ((type_declr | globals | native_func_declr) NEWLINE)* (func NEWLINE)*


  // Declarations

  type_declr        : KTYPE ID EXTENDS (HANDLE | ID)

  globals           : GLOBALS NEWLINE global_var_declr* ENDGLOBALS

  global_var_declr  : (CONSTANT TYPE ID EQUALS expr NEWLINE | _var_declr NEWLINE)

  native_func_declr : CONSTANT? NATIVE func_declr

  func_declr        : ID TAKES (NOTHING | TYPE ID (COMMA TYPE ID)*) RETURNS (NOTHING | TYPE)

  local_var_declr   : LOCAL _var_declr

  _var_declr        : TYPE ID (EQUALS expr)? | TYPE ARRAY ID


  // Functions

  func : CONSTANT? FUNCTION func_declr NEWLINE (local_var_declr NEWLINE)* (statement NEWLINE)* ENDFUNCTION

  args : expr (COMMA expr)*


  // Statements

  statement   : set | call | ifthenelse | loop | return | debug

  set         : SET ID EQUALS expr | SET ID LBRACKET expr RBRACKET EQUALS expr

  call        : CALL func_call

  ifthenelse  : IF expr THEN NEWLINE (statement NEWLINE)* (ELSEIF expr THEN NEWLINE (statement NEWLINE)*)* (ELSE NEWLINE (statement NEWLINE)*)? ENDIF

  loop        : LOOP NEWLINE (statement NEWLINE | EXITWHEN expr NEWLINE)* ENDLOOP

  return      : RETURN expr?

  debug       : DEBUG (set | call | ifthenelse | loop)


  // Expressions

  expr      : binary_op | unary_op | func_call | array_ref | func_ref | ID | _const | parens

  binary_op : expr (PLUS | MINUS | TIMES | DIVIDE | EQ | NE | LT | GT | LE | GE | AND | OR) expr

  unary_op  : (PLUS | MINUS | NOT) expr

  func_call : ID LPARENS args? RPARENS

  array_ref : ID LBRACKET expr RBRACKET

  func_ref  : FUNCTION ID

  _const    : REAL_CONST | INT_CONST_HEX | INT_CONST_OCT | INT_CONST_DEC | INT_LITERAL | BOOL_CONST | STRING_LITERAL | NULL_CONST

  parens    : LPARENS expr RPARENS


  NEWLINE    : /([\\r]?[\\n])+/
  WHITESPACE : /[ \\t\\f\\r\\n]+/
  COMMENT    : /\\/\\/[^\\n]*/

  %ignore COMMENT
  %ignore WHITESPACE
"""

JassParser = Lark(grammar, parser="lalr")
