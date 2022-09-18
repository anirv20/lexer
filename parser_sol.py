from ast import NotEq
from lib2to3.pgen2.tokenize import TokenError
import numbers
from lexer import Lexer, Tokentype, SyntaxErrorException
from astree import *

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
        node = self.program()
        return node
    
    def literal(self):
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

    def fexpr(self):
        if self.peek().type == Tokentype.ParenthesisL:
            if self.match_if(Tokentype.Identifier):
                self.match(Tokentype.ParenthesisL)
                self.args()
                self.match(Tokentype.ParenthesisR)
        else:
            self.pexpr()
    
    def i_or_f(self):
        self.match(Tokentype.Identifier)
        if self.match_if(Tokentype.ParenthesisL):
            if self.match_if(Tokentype.ParenthesisR):
                pass
            else:
                self.args()


    def mi_expr_m(self):
        if self.match_if(Tokentype.Period):
            self.i_or_f()
            self.mi_expr_m()
        elif self.match_if(Tokentype.BracketL):
            self.expr()
            self.match(Tokentype.BracketR)
            self.mi_expr_m()
        else:
            pass #eps

    def mi_expr(self):
        self.fexpr()
        self.mi_expr_m()

    def uexpr(self):
        if self.match_if(Tokentype.OpMinus):
            self.uexpr()
        else:
            self.mi_expr()
            
    def mul_op(self):
        if self.match_if(Tokentype.OpMultiply):
            return True
        elif self.match_if(Tokentype.OpIntDivide):
            return True
        elif self.match_if(Tokentype.OpModulus):
            return True
        else:
            return False

    def mexpr_m(self):
        if self.mul_op():
            self.uexpr()
            self.mexpr_m()   

    def mexpr(self):
        self.uexpr()
        self.mexpr_m()

    def add_op(self):
        if self.match_if(Tokentype.OpPlus):
            return True
        elif self.match_if(Tokentype.OpMinus):
            return True
        else:
            return False

    def aexpr_m(self):
        if self.add_op():
            self.mexpr()
            self.aexpr_m()

    def aexpr(self):
        self.mexpr()
        self.aexpr_m()

    def rel_op(self):
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
        self.aexpr()
        if self.rel_op():
            self.aexpr()
    
    def not_expr(self):
        if self.match_if(Tokentype.OpNot):
            pass
        self.cexpr()

    def and_expr_m(self):
        if self.match_if(Tokentype.OpAnd):
            self.not_expr()
        
    def and_expr(self):
        self.not_expr()
        self.and_expr_m()

    def or_expr_m(self):
        if self.match_if(Tokentype.OpOr):
            self.and_expr
            self.or_expr_m
    
    def or_expr(self):
        self.and_expr()
        self.or_expr_m

    def expr(self):
        self.or_expr()
        if self.match_if(Tokentype.KwIf):
            self.expr()
            self.match(Tokentype.KwElse)
            self.expr()
            
    def lexpr(self):
        if self.match_if(Tokentype.BracketL):
            self.args()
            self.match(Tokentype.BracketR)
        elif self.match_if(Tokentype.Identifier):
            pass
        else:
            self.literal()
    
    def pexpr(self):
        if self.match_if(Tokentype.ParenthesisL):
            self.expr()
            self.match(Tokentype.ParenthesisR)
        else:
            self.lexpr()

    def args(self):
        self.expr()
        if self.match_if(Tokentype.Comma):
            self.args()

    def stmt(self):
        if self.token.type == Tokentype.KwIf:
            self.if_stmt()
        elif self.token.type == Tokentype.KwWhile:
            self.wh_stmt()
        elif self.token.type == Tokentype.KwFor:
            self.for_stmt()
        else:
            self.si_stmt()
            self.match(Tokentype.Newline)

    def stmts_m(self):
        if self.token.type in [Tokentype.KwIf, Tokentype.KwWhile, Tokentype.KwFor, Tokentype.Identifier, Tokentype.KwPass, Tokentype.KwReturn, Tokentype.OpNot, Tokentype.OpMinus]:
            self.stmt()
            self.stmts_m()
        else:
            pass

    def stmts(self):
        self.stmt()
        self.stmts_m()

    def block(self):
        self.match(Tokentype.Newline)
        self.match(Tokentype.Indent)
        self.stmts()
        self.match(Tokentype.Dedent)
    
    def target_m(self):
        if self.match_if(Tokentype.Period):
            self.match(Tokentype.Identifier)
            self.target_m()
        elif self.match_if(Tokentype.BracketL):
            self.expr()
            self.match(Tokentype.BracketR)
            self.target_m()

    def target(self):
        if self.match_if(Tokentype.Identifier):
            self.target_m()
        else:
            self.cexpr()
            self.target_m()
    
    def asgn_stmt_m(self):
        if self.match_if(Tokentype.OpAssign):
            self.target()
            self.asgn_stmt_m()
        
    def asgn_stmt(self):
        self.target()
        if self.match_if(Tokentype.OpAssign):
            self.expr()
            self.asgn_stmt_m()
            return True
        else:
            return False
    
    def asgn_stmts_m(self):
        if self.asgn_stmt():
            self.asgn_stmts_m()
    
    def asgn_stmts(self):
        self.asgn_stmt()
        self.asgn_stmts_m()

    def si_stmt(self):
        if self.match_if(Tokentype.KwPass):
            pass
        elif self.match_if(Tokentype.KwReturn):
            if self.token.type != Tokentype.Newline:
               self.expr()
        else:
            self.expr()
        # TODO: how to know if it is an expr or asgn_stmt? can't only use peek


    def for_stmt(self):
        self.match(Tokentype.KwFor)
        self.match(Tokentype.Identifier)
        self.match(Tokentype.OpIn)
        self.expr()
        self.match(Tokentype.Colon)
        self.block()

    def wh_stmt(self):
        self.match(Tokentype.KwWhile)
        self.expr()
        self.match(Tokentype.Colon)
        self.block()

    def elif_stmt(self):
        self.match(Tokentype.KwElif)
        self.expr()
        self.match(Tokentype.Colon)
        self.block()

    def elif_stmts_m(self):
        if self.token.type == Tokentype.KwElif:
            self.elif_stmts()
            self.elif_stmts_m()
        else:
            pass #eps

    def elif_stmts(self):
        self.elif_stmt()
        self.elif_stmts_m()
    
    def if_stmt(self):
        self.match(Tokentype.KwIf)
        self.expr()
        self.match(Tokentype.Colon)
        self.if_block()
        if self.match_if(Tokentype.KwElse):
            self.block()

    def if_block(self):
        self.block()
        self.elif_stmts_m()
    
    def var_def(self):
        self.typed_var()
        self.match(Tokentype.OpAssign)
        self.literal()
        self.match(Tokentype.Newline)

    def nonloc_decl(self):
        self.match(Tokentype.KwNonLocal)
        self.match(Tokentype.Identifier)
        self.match(Tokentype.Newline)

    def global_decl(self):
        self.match(Tokentype.KwGlobal)
        self.match(Tokentype.Identifier)
        self.match(Tokentype.Newline)

    def type(self):
        name = self.token.lexeme
        if self.match_if(Tokentype.Identifier):
            node = ClassTypeAnnotationNode(name)
        elif self.match_if(Tokentype.StringLiteral):
            node = ClassTypeAnnotationNode(name)
        else:
            self.match(Tokentype.BracketL)
            sub_node = self.type()
            self.match(Tokentype.BracketR)
            node = ListTypeAnnotationNode(sub_node)
        return node


    def typed_var(self):
        id_node = IdentifierNode(self.token.lexeme)
        self.match(Tokentype.Identifier)
        self.match(Tokentype.Colon)
        type_node = self.type()
        return TypedVarNode(id_node, type_node)
        
    def all_decl(self):
        if self.token.type == Tokentype.KwGlobal:
            self.global_decl()
        elif self.token.type == Tokentype.KwNonLocal:
            self.nonloc_decl()
        elif self.token.type == Tokentype.KwDef:
            self.func_def()
        else:
            self.var_def()
    
    def all_decls_m(self):
        if self.token.type in [Tokentype.KwGlobal, Tokentype.KwNonLocal, Tokentype.KwDef, Tokentype.Identifier]:
            self.all_decl()
            self.all_decls_m()
        else:
            pass #eps

    def all_decls(self):
        self.all_decl()
        self.all_decls_m()

    def func_body(self):
        decls = [Tokentype.KwGlobal, Tokentype.KwNonLocal, Tokentype.KwDef, Tokentype.Identifier]
        if self.token.type in decls :
            self.all_decls()
            self.stmts()
        else:
            self.stmts()
        return None, None  
        
    
    def typed_args(self):
        typed_args = [self.typed_var()]
        if self.match_if(Tokentype.Comma):
            typed_args.append(self.typed_args())
        return typed_args


    def func_def(self):
        self.match(Tokentype.KwDef)
        name = self.token.lexeme
        self.match(Tokentype.Identifier)
        self.match(Tokentype.ParenthesisL)
        if self.match_if(Tokentype.ParenthesisR):
            pass
        else:
            param_list = self.typed_args()
            self.match(Tokentype.ParenthesisR)
#        param_list = [] if not param_list else param_list
        if self.match_if(Tokentype.Arrow):
            return_type = self.type()
        self.match(Tokentype.Colon)
        self.match(Tokentype.Newline)
        self.match(Tokentype.Indent)
        decls, stmts = self.func_body()
        self.match(Tokentype.Dedent)
        return FuncDefNode(name, param_list, return_type, decls, stmts)

    def vf_def(self):
        if self.token.type == Tokentype.KwDef:
            self.func_def()
        else:
            self.var_def()

    def vf_defs_m(self):
        if self.token.type in [Tokentype.KwDef, Tokentype.Identifier]:
            self.vf_def()
            self.vf_defs_m()
            
    def vf_defs(self):
        self.vf_def()
        self.vf_defs_m()
    
    def class_body(self):
        if self.match_if(Tokentype.KwPass):
            self.match(Tokentype.Newline)
        else:
            self.vf_defs()

    def class_def(self):
        match_tokens = [Tokentype.KwClass, Tokentype.Identifier, Tokentype.ParenthesisL, Tokentype.Identifier,
            Tokentype.ParenthesisR, Tokentype.Colon, Tokentype.Newline, Tokentype.Indent]
        for token in match_tokens:
            self.match(token)
        self.class_body()
        self.match(Tokentype.Dedent)
    
    def vfc_def(self):
        if self.token.type == Tokentype.KwDef:
            node = self.func_def()
        elif self.token.type == Tokentype.KwClass:
            node = self.class_def()
        else:
            node = self.var_def()
        return node

    def vfc_defs_m(self):
        nodes = list()
        if self.token.type in [Tokentype.KwDef, Tokentype.KwClass, Tokentype.Identifier]:
            nodes.append(self.vfc_def())
            nodes.append(self.vfc_defs_m())
        else:
            pass #eps
        return nodes

    def vfc_defs(self):
        vfc_defs = list()
        vfc_defs.append(self.vfc_def())
        vfc_defs.append(self.vfc_defs_m())
        return vfc_defs

    def program(self):
        stmts = list()
        vfc_defs = list()
        if self.token.type in [Tokentype.KwClass, Tokentype.KwDef, Tokentype.Identifier]:
            vfc_defs = self.vfc_defs()
            if self.token.type not in [Tokentype.KwClass, Tokentype.KwDef, Tokentype.Identifier]: # check if stmt?
                if self.match_if(Tokentype.EOI):
                    pass
                else:
                    stmts = self.stmts()
        elif self.match_if(Tokentype.EOI):
            pass
        else:
            stmts = self.stmts()
        return ProgramNode(vfc_defs, stmts)
     