from ast import NotEq
from lib2to3.pgen2.tokenize import TokenError
import numbers
from lexer import Lexer, Tokentype, SyntaxErrorException
import astree

class Parser:

    def __init__(self, f):
        self.lexer = Lexer(f)
        self.token = self.lexer.next()
        print(self.token)
        self.token_peek = None
        self.indentation = 0
        self.num_space = 2

    # Helper function.
    def match(self, type):
        if self.token.type == type:
            print(self.token)
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
        self.program()
        return None
    
    def literal(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "literal")
        if self.match_if(Tokentype.KwNone):
            pass
        elif self.match_if(Tokentype.BoolTrueLiteral):
            pass
        elif self.match_if(Tokentype.BoolFalseLiteral):
            pass
        elif self.match_if(Tokentype.IntegerLiteral):
            pass
        else:
            self.match(Tokentype.StringLiteral)
        self.indentation -= self.num_space

    def fexpr(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "fexpr")
        if self.peek().type == Tokentype.ParenthesisL:
            if self.match_if(Tokentype.Identifier):
                self.match(Tokentype.ParenthesisL)
                self.args()
                self.match(Tokentype.ParenthesisR)
        else:
            self.pexpr()
        self.indentation -= self.num_space
    
    def i_or_f(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "i or ")
        self.match(Tokentype.Identifier)
        if self.match_if(Tokentype.ParenthesisL):
            if self.match_if(Tokentype.ParenthesisR):
                pass
            else:
                self.args()

        self.indentation -= self.num_space

    def mi_expr_m(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "mi_expr_m")
        if self.match_if(Tokentype.Period):
            self.i_or_f()
            self.mi_expr_m()
        elif self.match_if(Tokentype.BracketL):
            self.expr()
            self.match(Tokentype.BracketR)
            self.mi_expr_m()
        else:
            pass #eps
        self.indentation -= self.num_space

    def mi_expr(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "mi_expr")
        self.fexpr()
        self.mi_expr_m()
        self.indentation -= self.num_space

    def uexpr(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "uexpr")
        if self.match_if(Tokentype.OpMinus):
            self.uexpr()
        else:
            self.mi_expr()

        self.indentation -= self.num_space
            
    def mul_op(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "mul_op")
        self.indentation -= self.num_space
        if self.match_if(Tokentype.OpMultiply):
            return True
        elif self.match_if(Tokentype.OpIntDivide):
            return True
        elif self.match_if(Tokentype.OpModulus):
            return True
        else:
            return False

    def mexpr_m(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "mexpr_m")
        if self.mul_op():
            self.uexpr()
            self.mexpr_m()   

        self.indentation -= self.num_space

    def mexpr(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "mexpr")
        self.uexpr()
        self.mexpr_m()
        self.indentation -= self.num_space

    def add_op(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "add_op")
        self.indentation -= self.num_space
        if self.match_if(Tokentype.OpPlus):
            return True
        elif self.match_if(Tokentype.OpMinus):
            return True
        else:
            return False

    def aexpr_m(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "aexpr_m")
        if self.add_op():
            self.mexpr()
            self.aexpr_m()
        self.indentation -= self.num_space

    def aexpr(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "aexpr")
        self.mexpr()
        self.aexpr_m()
        self.indentation -= self.num_space

    def rel_op(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "rel_op")
        self.indentation -= self.num_space
        if self.match_if(Tokentype.OpEq):
            return True
        elif self.match_if(Tokentype.OpNotEq):
            return True
        elif self.match_if(Tokentype.OpGt):
            return True
        elif self.match_if(Tokentype.OpGt):
            return True
        elif self.match_if(Tokentype.OpLtEq):
            return True
        elif self.match_if(Tokentype.OpGtEq):
            return True
        elif self.match_if(Tokentype.OpIs):
            return True
        else:
            return False


    def cexpr(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "cexpr")
        self.aexpr()
        if self.rel_op():
            self.aexpr()
        self.indentation -= self.num_space
    
    def not_expr(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "not_expr")
        if self.match_if(Tokentype.OpNot):
            pass
        self.cexpr()
        self.indentation -= self.num_space

    def and_expr_m(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "and_expr_m")
        if self.match_if(Tokentype.OpAnd):
            self.not_expr()
        self.indentation -= self.num_space
        
    def and_expr(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "and_expr")
        self.not_expr()
        self.and_expr_m()
        self.indentation -= self.num_space

    def or_expr_m(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "or_expr_m")
        if self.match_if(Tokentype.OpOr):
            self.and_expr
            self.or_expr_m
        self.indentation -= self.num_space
    
    def or_expr(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "or_expr")
        self.and_expr()
        self.or_expr_m
        self.indentation -= self.num_space

    def expr(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "expr")
        self.or_expr()
        if self.match_if(Tokentype.KwIf):
            self.expr()
            self.match(Tokentype.KwElse)
            self.expr()
        self.indentation -= self.num_space
            
    def lexpr(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "lexpr")
        if self.match_if(Tokentype.BracketL):
            self.args()
            self.match(Tokentype.BracketR)
        elif self.match_if(Tokentype.Identifier):
            pass
        else:
            self.literal()
        self.indentation -= self.num_space
    
    def pexpr(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "pexpr")
        if self.match_if(Tokentype.ParenthesisL):
            self.expr()
            self.match(Tokentype.ParenthesisR)
        else:
            self.lexpr()
        self.indentation -= self.num_space

    def args(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "args")
        self.expr()
        if self.match_if(Tokentype.Comma):
            self.args()
        self.indentation -= self.num_space

    def stmt(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "stmt")
        if self.token.type == Tokentype.KwIf:
            self.if_stmt()
        elif self.token.type == Tokentype.KwWhile:
            self.wh_stmt()
        elif self.token.type == Tokentype.KwFor:
            self.for_stmt()
        else:
            self.si_stmt()
            self.match(Tokentype.Newline)
        self.indentation -= self.num_space

    def stmts_m(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "stmts_m")
        if self.token.type in [Tokentype.KwIf, Tokentype.KwWhile, Tokentype.KwFor, Tokentype.Identifier, Tokentype.KwPass, Tokentype.KwReturn, Tokentype.OpNot, Tokentype.OpMinus]:
            self.stmt()
            self.stmts_m()
        else:
            pass
        self.indentation -= self.num_space

    def stmts(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "stmts")
        self.stmt()
        self.stmts_m()
        self.indentation -= self.num_space

    def block(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "block")
        self.match(Tokentype.Newline)
        self.match(Tokentype.Indent)
        self.stmts()
        self.match(Tokentype.Dedent)
        self.indentation -= self.num_space
    
    def target_m(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "target_m")
        if self.match_if(Tokentype.Period):
            self.match(Tokentype.Identifier)
            self.target_m()
        elif self.match_if(Tokentype.BracketL):
            self.expr()
            self.match(Tokentype.BracketR)
            self.target_m()
        self.indentation -= self.num_space

    def target(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "target")
        if self.match_if(Tokentype.Identifier):
            self.target_m()
        else:
            self.cexpr()
            self.target_m()
        self.indentation -= self.num_spa
    
    def asgn_stmt_m(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "asgn_stmt_m")
        if self.match_if(Tokentype.OpAssign):
            self.target()
            self.asgn_stmt_m()
        self.indentation -= self.num_space
        
    def asgn_stmt(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "asgn_stmt")
        self.target()
        if self.match_if(Tokentype.OpAssign):
            self.expr()
            self.asgn_stmt_m()
            self.indentation -= self.num_space
            return True
        else:
            self.indentation -= self.num_space
            return False
    
    def asgn_stmts_m(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "asgn_stmts_m")
        if self.asgn_stmt():
            self.asgn_stmts_m()
        self.indentation -= self.num_space
    
    def asgn_stmts(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "asgn_stmts")
        self.asgn_stmt()
        self.asgn_stmts_m()
        self.indentation -= self.num_space

    def si_stmt(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "si_stmt")
        if self.match_if(Tokentype.KwPass):
            pass
        elif self.match_if(Tokentype.KwReturn):
            if self.token.type != Tokentype.Newline:
               self.expr()
        else:
            self.expr()
        self.indentation -= self.num_space
        # TODO: how to know if it is an expr or asgn_stmt? can't only use peek


    def for_stmt(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "for_stmts")
        self.match(Tokentype.KwFor)
        self.match(Tokentype.Identifier)
        self.match(Tokentype.OpIn)
        self.expr()
        self.match(Tokentype.Colon)
        self.block()
        self.indentation -= self.num_space

    def wh_stmt(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "wh_stmt")
        self.match(Tokentype.KwWhile)
        self.expr()
        self.match(Tokentype.Colon)
        self.block()
        self.indentation -= self.num_space

    def elif_stmt(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "elif_stmt")
        self.match(Tokentype.KwElif)
        self.expr()
        self.match(Tokentype.Colon)
        self.block()
        self.indentation -= self.num_space

    def elif_stmts_m(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "elif_stmts_m")
        if self.token.type == Tokentype.KwElif:
            self.elif_stmts()
            self.elif_stmts_m()
        else:
            pass #eps
        self.indentation -= self.num_space

    def elif_stmts(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "elif_stmts")
        self.elif_stmt()
        self.elif_stmts_m()
        self.indentation -= self.num_space
    
    def if_stmt(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "if_stmt")
        self.match(Tokentype.KwIf)
        self.expr()
        self.match(Tokentype.Colon)
        self.if_block()
        if self.match_if(Tokentype.KwElse):
            self.block()
        self.indentation -= self.num_space

    def if_block(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "if_block")
        self.block()
        self.elif_stmts_m()
        self.indentation -= self.num_space
    
    def var_def(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "var_def")
        self.typed_var()
        self.match(Tokentype.OpAssign)
        self.literal()
        self.match(Tokentype.Newline)
        self.indentation -= self.num_space

    def nonloc_decl(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "nonloc_decl")
        self.match(Tokentype.KwNonLocal)
        self.match(Tokentype.Identifier)
        self.match(Tokentype.Newline)
        self.indentation -= self.num_space

    def global_decl(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "global_decl")
        self.match(Tokentype.KwGlobal)
        self.match(Tokentype.Identifier)
        self.match(Tokentype.Newline)
        self.indentation -= self.num_space

    def type(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "type")
        if self.match_if(Tokentype.Identifier):
            pass
        elif self.match_if(Tokentype.StringLiteral):
            pass
        else:
            self.match(Tokentype.BracketL)
            self.type()
            self.match(Tokentype.BracketR)  
        self.indentation -= self.num_space


    def typed_var(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "typed_var")
        self.match(Tokentype.Identifier)
        self.match(Tokentype.Colon)
        self.type()
        self.indentation -= self.num_space
        
    def all_decl(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "all_decl")
        if self.token.type == Tokentype.KwGlobal:
            self.global_decl()
        elif self.token.type == Tokentype.KwNonLocal:
            self.nonloc_decl()
        elif self.token.type == Tokentype.KwDef:
            self.func_def()
        else:
            self.var_def()
        self.indentation -= self.num_space
    
    def all_decls_m(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "all_decls_m")
        #self.peek()
        if self.token.type in [Tokentype.KwGlobal, Tokentype.KwNonLocal, Tokentype.KwDef, Tokentype.Identifier]:
            self.all_decl()
            self.all_decls_m()
        else:
            pass #eps
        self.indentation -= self.num_space
            

    def all_decls(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "all_decls")
        self.all_decl()
        self.all_decls_m()
        self.indentation -= self.num_space


    def func_body(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "func_body")
        decls = [Tokentype.KwGlobal, Tokentype.KwNonLocal, Tokentype.KwDef, Tokentype.Identifier]
        if self.token.type in decls :
            self.all_decls()
            self.stmts()
        else:
            self.stmts()
        self.indentation -= self.num_space    
        
    
    def typed_args(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "typed_args")
        self.typed_var()
        if self.match_if(Tokentype.Comma):
            self.typed_args()
        self.indentation -= self.num_space


    def func_def(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "func_def")
        self.match(Tokentype.KwDef)
        self.match(Tokentype.Identifier)
        self.match(Tokentype.ParenthesisL)
        if self.match_if(Tokentype.ParenthesisR):
            pass
        else:
            self.typed_args()
            self.match(Tokentype.ParenthesisR)
        if self.match_if(Tokentype.Arrow):
            self.type()
        self.match(Tokentype.Colon)
        self.match(Tokentype.Newline)
        self.match(Tokentype.Indent)
        self.func_body()
        self.match(Tokentype.Dedent)
        self.indentation -= self.num_space

    def vf_def(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "vf_def")
        if self.token.type == Tokentype.KwDef:
            self.func_def()
        else:
            self.var_def()
        self.indentation -= self.num_space

    def vf_defs_m(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "vf_defs_m")
        if self.token.type in [Tokentype.KwDef, Tokentype.Identifier]:
            self.vf_def()
            self.vf_defs_m()
        self.indentation -= self.num_space
            
    def vf_defs(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "vf_defs")
        self.vf_def()
        self.vf_defs_m()
        self.indentation -= self.num_space
    
    def class_body(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "class_body")
        if self.match_if(Tokentype.KwPass):
            self.match(Tokentype.Newline)
        else:
            self.vf_defs()
        self.indentation -= self.num_space

    def class_def(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "class_def")
        match_tokens = [Tokentype.KwClass, Tokentype.Identifier, Tokentype.ParenthesisL, Tokentype.Identifier,
            Tokentype.ParenthesisR, Tokentype.Colon, Tokentype.Newline, Tokentype.Indent]
        for token in match_tokens:
            self.match(token)
        self.class_body()
        self.match(Tokentype.Dedent)
        self.indentation -= self.num_space
    
    def vfc_def(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "vfc_def")
        if self.token.type == Tokentype.KwDef:
            self.func_def()
        elif self.token.type == Tokentype.KwClass:
            self.class_def()
        else:
            self.var_def()
        self.indentation -= self.num_space

    def vfc_defs_m(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "vfc_defs_m")
        if self.token.type in [Tokentype.KwDef, Tokentype.KwClass, Tokentype.Identifier]:
            self.vfc_def()
            self.vfc_defs_m()
        else:
            pass #eps
        self.indentation -= self.num_space

    def vfc_defs(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "vfc_defs")
        print("vfc_defs")
        self.vfc_def()
        self.vfc_defs_m()
        self.indentation -= self.num_space

    def program(self):
        self.indentation += self.num_space
        print(" " * self.indentation, "program")
        if self.token.type in [Tokentype.KwClass, Tokentype.KwDef, Tokentype.Identifier]:
            self.vfc_defs()
            if self.token.type not in [Tokentype.KwClass, Tokentype.KwDef, Tokentype.Identifier]: # check if stmt?
                if self.match_if(Tokentype.EOI):
                    pass
                else:
                    self.stmts()
        elif self.match_if(Tokentype.EOI):
            print("End of file")
            pass
        else:
            self.stmts()
        self.indentation -= self.num_space
     