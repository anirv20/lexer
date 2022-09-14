#
# A recursive-descent parser for parsing boolean expressions.
#
# E -> E or E | E and E | not E | ( E ) | True | False

# 1. Rewrite your grammar to be suitable for recursive-descent parsing:
#
"""
    E -> E or E | E and E | not E | ( E ) | True | False

    becomes:

    E -> E or A | A
    A -> A and N | N
    N -> not N | B
    B -> True | False | ( E )

    becomes:
    
    S -> E eoi
    
    E -> A E'
    E' -> or A E' | eps
    A -> N A'
    A' -> and N A' | eps
    N -> not N | B
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
            print("Matched ", self.token.type)
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

    #E -> A E'
    def expr(self):
        self.expr_and()
        self.expr_marked()

    # E' -> or A E' | eps
    def expr_marked(self):
        if self.match_if(Tokentype.OpOr):
            self.expr_and()
            self.expr_marked()
    
    #A -> N A'
    def expr_and(self):
        self.expr_not()
        self.expr_and_marked()

    # A' -> and N A' | eps
    def expr_and_marked(self):
        if self.match_if(Tokentype.OpAnd):
            self.expr_not()
            self.expr_and_marked()
    
    #N -> not N | B
    def expr_not(self):
        if self.match_if(Tokentype.OpNot):
            self.expr_not()
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


