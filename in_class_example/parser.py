from lexer_sol import Lexer, Tokentype, SyntaxErrorException
import ast


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
    # The file should return an AST if parsing is successful, otherwise a syntax-error exception is thrown.
    def parse(self):
        node = self.sexpr()
        self.match(Tokentype.EOI)
        return node

    #  1 + 2 + 3
    #        +            +
    #       /\           1   +
    #      +  3             2  3
    #     /\
    #    1  2

    #
    # foo.a.b.c(1,2).d[2].e(4,5)[3]  OK
    # (((((foo.a).b).c(1,2)).d)[2]).e(4,5)[3]  left-associative
    # e(4,5)[3] OK
    # f[3](6,7) NOT OK in ChocoPy

    # cexpr     -> aexpr rel_op aexpr | aexpr
    # rel_op    -> == | != | ... | is
    # aexpr     -> aexpr add_op mexpr | mexpr
    # add_op    -> + | -
    # mexpr     -> mexpr mul_op uexpr | uexpr
    # mul_op    -> * | // | %
    # uexpr     -> - uexpr | mi_expr
    # mi_expr   -> mi_expr . i_or_f | mi_expr [ expr ] | fexpr
    # i_or_f    -> ID | ID '(' arguments ')'
    # fexpr     -> ...

    # cexpr     -> aexpr [ rel_op aexpr ]
    # aexpr     -> mexpr { add_op mexpr }
    # mexpr     -> uexpr { mul_op uexpr }
    # mi_expr   -> fexpr { . i_or_f | '[' expr ']' }
    # i_or_f    -> ID [ '(' arguments ')' ]

    # Exercise:   1 + 2 > 5 - 4
    #
    #                >
    #            +        -
    #          1   2     5  4

    # sexpr     -> aexpr [ rel_op aexpr ]
    # rel_op    -> > | <
    # aexpr     -> INT { add_op INT }
    # add_op    -> + | -
    def sexpr(self):
        opmap = {Tokentype.OpGt: ast.Operator.Gt,
                 Tokentype.OpLt: ast.Operator.Lt}
        node = self.aexpr()
        if self.token.type in opmap.keys():
            op = opmap[self.token.type]
            self.match(self.token.type)
            rhs = self.aexpr()
            node = ast.BinaryOpNode(op, node, rhs)
        return node

    def aexpr(self):
        ops = [Tokentype.OpPlus, Tokentype.OpMinus]
        opmap = {Tokentype.OpPlus: ast.Operator.Plus,
                 Tokentype.OpMinus: ast.Operator.Minus}
        lexeme = self.token.lexeme
        self.match(Tokentype.IntegerLiteral)
        node = ast.IntegerLiteral(int(lexeme))
        while self.token.type in ops:
            op = opmap[self.token.type]
            self.match(self.token.type)
            lexeme = self.token.lexeme
            self.match(Tokentype.IntegerLiteral)
            rhs = ast.IntegerLiteral(int(lexeme))
            node = ast.BinaryOpNode(op, node, rhs)
        return node
