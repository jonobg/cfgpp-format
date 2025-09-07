grammar Cfgpp;

// Parser rules
config: object EOF;

object: IDENTIFIER '(' parameterList? ')' ( '{' objectBody '}' )?;

parameterList: parameter (',' parameter)*;

parameter: type IDENTIFIER ('=' value)?;

type: IDENTIFIER ('[]')?;

value: STRING | NUMBER | BOOLEAN | array | object;

array: '[' (value (',' value)*)? ']';

objectBody: (object ';'?)*;

// Lexer rules
IDENTIFIER: [a-zA-Z_][a-zA-Z0-9_]*;
STRING: '"' .*? '"';
NUMBER: '-'? [0-9]+ ('.' [0-9]+)?;
BOOLEAN: 'true' | 'false';

WHITESPACE: [ \t\r\n]+ -> skip;
COMMENT: '//' ~[\r\n]* -> skip;
MULTILINE_COMMENT: '/*' .*? '*/' -> skip;
