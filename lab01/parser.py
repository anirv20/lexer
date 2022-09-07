#
# A recursive-descent parser for parsing boolean expressions.
#
# E -> E or E | E and E | not E | ( E ) | True | False

# 1. Rewrite your grammar to be suitable for recursive-descent parsing:
#
"""
    E -> E or E | E and E | not E | ( E ) | True | False

    becomes:

    S -> E eoi
    E -> E' or E | E'
    E' -> E'' and E' | E''
    E'' -> not E | B
    B -> True | False | ( E )

"""

from lexer import Lexer, Tokentype, SyntaxErrorException

class Parser:

    def __init__(self, f):
        self.lexer = Lexer(f)
        self.token = self.lexer.next()

    # Helper function.
    def match(self, type):
        if self.token.type == type:
            self.token = self.lexer.next()
        else:
            text = "Syntax error: expected {:s} but got {:s} ({:s}).".format(
                type, self.token.type, self.token.lexeme
            )
            raise SyntaxErrorException(text, self.token.location)

    # Helper function
    def match_if(self, type):
        if self.token.type == type:
            self.match(type)
            return True
        return False

    # Finish implementing the parser. A call to parse, parses a single Boolean expression.
    #S -> E eoi
    def parse(self):
        self.expr()
        self.match(Tokentype.EOI)

    #E -> E' or E | E'
    def expr(self):
        self.expr1()
        if self.match_if(Tokentype.OpOr):
            self.expr()
    
    #E' -> E'' and E' | E''
    def expr1(self):
        self.expr2()
        if self.match_if(Tokentype.OpAnd):
            self.expr1()
    
    # E'' -> not E | B
    def expr2(self):
        if self.match_if(Tokentype.OpNot):
            self.expr()
        else:
            self.bool()
    
    # B -> True | False | ( E )
    def bool(self):
        if self.match_if(Tokentype.ParenthesisL):
            self.expr()
            self.match(Tokentype.ParenthesisR)
        elif self.match_if(Tokentype.BoolTrueLiteral):
            pass
        else:
            self.match(Tokentype.BoolFalseLiteral)


