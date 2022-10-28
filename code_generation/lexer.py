from enum import Enum
from typing import NamedTuple
import error


# The token types the Lexer recognizes.
class Tokentype(Enum):
    EOI = 0  # end of input
    Unknown = 1  # unknown

    # Keywords
    KwPass = 3  # pass
    KwIf = 10  # if
    KwElif = 11  # elif
    KwElse = 12  # else
    KwWhile = 14  # while
    KwDef = 16  # def
    KwReturn = 17  # return

    # Operators
    OpOr = 30  # or
    OpAnd = 31  # and
    OpNot = 32  # not

    OpPlus = 35  # +
    OpMinus = 36  # -
    OpMultiply = 37  # *
    OpIntDivide = 38  # //
    OpModulus = 39  # %

    OpLt = 40  # <
    OpGt = 41  # >
    OpLtEq = 42  # <=
    OpGtEq = 43  # >=
    OpEq = 44  # ==
    OpNotEq = 45  # !=
    OpAssign = 46  # =

    # Punctuation marks
    ParenthesisL = 47  # (
    ParenthesisR = 48  # )
    Comma = 51  # ,
    Colon = 52  # :
    Arrow = 54  # ->

    # Other
    BoolTrueLiteral = 55  # True
    BoolFalseLiteral = 56  # False
    IntegerLiteral = 57  # digits (see project description)
    Identifier = 59  # name (see project description)
    Indent = 60  # indentation
    Dedent = 61  # dedentation
    Newline = 62  # newline


class Location(NamedTuple):
    line: int
    col: int


class Token(NamedTuple):
    type: Tokentype
    lexeme: str
    location: Location


class Lexer:
    # Private map of reserved words.
    __reserved_words = {
        "pass": Tokentype.KwPass,
        "if": Tokentype.KwIf,
        "elif": Tokentype.KwElif,
        "else": Tokentype.KwElse,
        "while": Tokentype.KwWhile,
        "def": Tokentype.KwDef,
        "return": Tokentype.KwReturn,
        "or": Tokentype.OpOr,
        "and": Tokentype.OpAnd,
        "not": Tokentype.OpNot,
        "True": Tokentype.BoolTrueLiteral,
        "False": Tokentype.BoolFalseLiteral
    }

    def __read_next_char(self):
        """
        Private helper routine. Reads the next input character, while keeping
        track of its location within the input file.
        """
        if self.eof:
            self.ch = ''
            return

        if self.ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        self.ch = self.f.read(1)

        if not self.ch:  # eof
            self.ch = '\n'
            self.line += 1
            self.col = 1
            self.eof = True

    def __init__(self, f):
        """
        Constructor for the lexer.
        :param: f handle to the input file (from open('filename')).
        """
        self.f, self.ch, self.line, self.col = f, '', 1, 0
        self.legal_indent_levels = [1]
        self.beginning_of_logical_line = True
        self.eof = False
        self.__read_next_char()  # Read in the first input character (self.ch).

    def next(self):
        """
        Match the next token in input.
        :return: Token with information about the matched Tokentype.
        """

        # Remove spaces, tabs, comments, and "empty" lines, if any, before matching the next Tokentype.
        bf_loc = Location(self.line, self.col)
        removed = True
        while removed:
            removed = False
            white_spaces = {' ', '\t', '\r'}
            while self.ch in white_spaces:
                self.__read_next_char()
                removed = True
            if self.ch == '#':
                while self.ch and self.ch not in {'\n'}:
                    self.__read_next_char()
                removed = True
            if bf_loc.col == 1 and self.ch == '\n':  # Lines with only ws and comments are ignored.
                self.__read_next_char()
                removed = True

        # Record the start location of the lexeme we're matching.
        loc = Location(self.line, self.col)

        # Ensure indentation is correct, emitting (returning) an INDENT/DEDENT token if called for.
        if self.beginning_of_logical_line:  # At start of a logical line.
            self.beginning_of_logical_line = False
            if loc.col > self.legal_indent_levels[-1]:
                self.legal_indent_levels.append(loc.col)
                return Token(Tokentype.Indent, '<INDENT>', loc)
            elif loc.col < self.legal_indent_levels[-1]:
                self.legal_indent_levels.pop()
                if loc.col > self.legal_indent_levels[-1]:
                    raise error.SyntaxErrorException(
                        'IndentationError: dedent does not match any outer indentation level', loc)
                self.beginning_of_logical_line = True
                return Token(Tokentype.Dedent, '<DEDENT>', loc)

        # Now, try to match a lexeme.
        if self.ch == '':
            token = Token(Tokentype.EOI, '', loc)
        elif self.ch == '<':
            self.__read_next_char()
            if self.ch == '=':
                token = Token(Tokentype.OpLtEq, '<=', loc)
                self.__read_next_char()
            else:
                token = Token(Tokentype.OpLt, '<', loc)
        elif self.ch == '>':
            self.__read_next_char()
            if self.ch == '=':
                token = Token(Tokentype.OpGtEq, '>=', loc)
                self.__read_next_char()
            else:
                token = Token(Tokentype.OpGt, '>', loc)
        elif self.ch == '+':
            token = Token(Tokentype.OpPlus, self.ch, loc)
            self.__read_next_char()
        elif self.ch == '-':
            self.__read_next_char()
            if self.ch == '>':
                token = Token(Tokentype.Arrow, '->', loc)
                self.__read_next_char()
            else:
                token = Token(Tokentype.OpMinus, '-', loc)
        elif self.ch == '*':
            token = Token(Tokentype.OpMultiply, self.ch, loc)
            self.__read_next_char()
        elif self.ch == '/':
            self.__read_next_char()
            if self.ch == '/':
                token = Token(Tokentype.OpIntDivide, '//', loc)
                self.__read_next_char()
            else:
                token = Token(Tokentype.Unknown, '/', loc)
        elif self.ch == '%':
            token = Token(Tokentype.OpModulus, self.ch, loc)
            self.__read_next_char()
        elif self.ch == '=':
            self.__read_next_char()
            if self.ch == '=':
                token = Token(Tokentype.OpEq, '==', loc)
                self.__read_next_char()
            else:
                token = Token(Tokentype.OpAssign, '=', loc)
        elif self.ch == '!':
            self.__read_next_char()
            if self.ch == '=':
                token = Token(Tokentype.OpNotEq, '!=', loc)
                self.__read_next_char()
            else:
                token = Token(Tokentype.Unknown, '!', loc)
        elif self.ch == '(':
            token = Token(Tokentype.ParenthesisL, self.ch, loc)
            self.__read_next_char()
        elif self.ch == ')':
            token = Token(Tokentype.ParenthesisR, self.ch, loc)
            self.__read_next_char()
        elif self.ch == ',':
            token = Token(Tokentype.Comma, self.ch, loc)
            self.__read_next_char()
        elif self.ch == ':':
            token = Token(Tokentype.Colon, self.ch, loc)
            self.__read_next_char()
        elif self.ch == '\n':
            self.beginning_of_logical_line = True
            token = Token(Tokentype.Newline, self.ch, loc)
            self.__read_next_char()
        else:
            if ('a' <= self.ch <= 'z') or ('A' <= self.ch <= 'Z') or (self.ch == '_'):
                # Match an identifier.
                chars = [self.ch]
                self.__read_next_char()
                while ('a' <= self.ch <= 'z') or ('A' <= self.ch <= 'Z') or (self.ch == '_') or ('0' <= self.ch <= '9'):
                    chars.append(self.ch)
                    self.__read_next_char()
                name = ''.join(chars)
                token = Token(self.__reserved_words.get(name, Tokentype.Identifier), name, loc)
            elif '0' <= self.ch <= '9':
                # Match a number literal.
                chars = [self.ch]
                self.__read_next_char()
                if chars[0] == '0' and ('0' <= self.ch <= '9'):
                    raise error.SyntaxErrorException("Leading zeros in decimal integer literals are not permitted", loc)
                while '0' <= self.ch <= '9':
                    chars.append(self.ch)
                    self.__read_next_char()
                token = Token(Tokentype.IntegerLiteral, ''.join(chars), loc)
                if int(token.lexeme) > 2147483647:
                    raise error.SyntaxErrorException("Integer literal overflow (> 2147483647)", loc)
            else:
                token = Token(Tokentype.Unknown, self.ch, loc)
                self.__read_next_char()

        return token
