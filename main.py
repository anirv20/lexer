#
# T-603-THYD Compilers
# Project: Test driver for lexer
#
from lexer import SyntaxErrorException
import lexer

filename = 'test.py'
with open(filename) as f:
    lex = lexer.Lexer(f)
    token = lex.next()
    while token.type != lexer.Tokentype.EOI:
        print(token.type, token.lexeme if token.type != lexer.Tokentype.Newline else "\\n", token.location.line)
        try:
            token = lex.next()
        except SyntaxErrorException as error:
            print(error)