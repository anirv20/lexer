from lexer import Lexer, Tokentype, SyntaxErrorException
import ast

class Parser:

    def __init__(self, f):
        self.lexer = Lexer(f)
        self.token = self.lexer.next()
        self.token_peek = None

    # Helper function.
    def match(self, type):
        if self.token.type == type:
            if self.token_peek is None:
                self.token = self.lexer.next()
            else:
                self.token = self.token_peek
                self.token_peek = None
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

    # Helper function
    def peek(self):
        if self.token_peek is None:
            self.token_peek = self.lexer.next()
        return self.token_peek

    # Finish implementing the parser. A call to parse, parses a single Boolean expression.
    # The file should return an AST if parsing is successful, otherwise a syntax-error exception is thrown.
    def parse(self):
        return None

    def lexpr(self):
        if self.match_if(Tokentype.BracketL):
            self.args()
            self.match(Tokentype.BracketR)
        elif self.match_if(Tokentype.Identifier):
            pass
        else:
            self.literal()

    def args(self):
        self.expr()
        if self.match_if(Tokentype.Comma):
            self.args()