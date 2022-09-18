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
        lexeme = self.token.lexeme
        if self.match_if(Tokentype.KwNone):
            node = NoneLiteralExprNode()
        elif self.match_if(Tokentype.BoolTrueLiteral):
            node = BooleanLiteralExprNode(True)
        elif self.match_if(Tokentype.BoolFalseLiteral):
            node = BooleanLiteralExprNode(False)
        elif self.match_if(Tokentype.IntegerLiteral):
            node = IntegerLiteralExprNode(int(lexeme))
        else:
            self.match(Tokentype.StringLiteral)
            node = StringLiteralExprNode(lexeme)
        return node

    def fexpr(self):
        lexeme = self.token.lexeme
        if self.peek().type == Tokentype.ParenthesisL:
            if self.match_if(Tokentype.Identifier):
                self.match(Tokentype.ParenthesisL)
                args = self.args() #list of exprnodes
                self.match(Tokentype.ParenthesisR)
                id_node = IdentifierNode(lexeme)
                node = FunctionCallExprNode(id_node, args)
        else:
            node = self.pexpr()
        return node
    
    def i_or_f(self):
        lexeme = self.token.lexeme
        self.match(Tokentype.Identifier)
        node = IdentifierNode(lexeme)
        if self.match_if(Tokentype.ParenthesisL):
            if self.match_if(Tokentype.ParenthesisR):
                pass
            else:
                args = self.args()
            id_node = IdentifierNode(lexeme)
            node = FunctionCallExprNode(id_node, args)
        return node

    def mi_expr_m(self):
        mi_exprs = []
        if self.match_if(Tokentype.Period):
            mi_exprs.append(self.i_or_f())
            mi_exprs.append(self.mi_expr_m())
        elif self.match_if(Tokentype.BracketL):
            mi_exprs.append(self.expr())
            self.match(Tokentype.BracketR)
            mi_exprs.append(self.mi_expr_m())
        else:
            pass #eps
        return mi_exprs

    def mi_expr(self):
        mi_expr = [self.fexpr()]
        mi_expr.append(self.mi_expr_m())
        return mi_expr

    def uexpr(self):
        nodes = []
        if self.match_if(Tokentype.OpMinus):
            nodes.append(self.uexpr())
        else:
            nodes.append(self.mi_expr())
        return nodes
            
    def mul_op(self):
        if self.match_if(Tokentype.OpMultiply):
            return Operator.Mult
        elif self.match_if(Tokentype.OpIntDivide):
            return Operator.IntDivide
        elif self.match_if(Tokentype.OpModulus):
            return Operator.Modulus

    def mexpr_m(self):
        if self.token.type in [Tokentype.OpMultiply, Tokentype.OpIntDivide, Tokentype.OpModulus]:
            op = self.mul_op()
            lhs = self.uexpr()
            rhs = self.mexpr_m()
            node = BinaryOpExprNode(op, lhs, rhs)
        return node


    def mexpr(self):
        exprs = []
        exprs.append(self.uexpr())
        exprs.append(self.mexpr_m())
        return exprs

    def add_op(self):
        if self.match_if(Tokentype.OpPlus):
            return Operator.Plus
        elif self.match_if(Tokentype.OpMinus):
            return Operator.Minus

    def aexpr_m(self):
        if self.token.lexeme in [Tokentype.OpPlus, Tokentype.OpMinus]:
            op = self.add_op()
            lhs = self.mexpr()
            rhs = self.aexpr_m()
            node = BinaryOpExprNode(op, lhs, rhs)
        return node


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
            node = self.if_stmt()
        elif self.token.type == Tokentype.KwWhile:
            node = self.wh_stmt()
        elif self.token.type == Tokentype.KwFor:
            node = self.for_stmt()
        else:
            node = self.si_stmt()
            self.match(Tokentype.Newline)
        return node

    def stmts_m(self):
        stmts = []
        if self.token.type in [Tokentype.KwIf, Tokentype.KwWhile, Tokentype.KwFor, Tokentype.Identifier, Tokentype.KwPass, Tokentype.KwReturn, Tokentype.OpNot, Tokentype.OpMinus]:
            stmts.append(self.stmt())
            stmts.append(self.stmts_m())
        else:
            pass
        return stmts

    def stmts(self):
        stmt_nodes = []
        stmt_nodes.append(self.stmt())
        stmt_nodes.append(self.stmts_m())
        return stmt_nodes

    def block(self):
        self.match(Tokentype.Newline)
        self.match(Tokentype.Indent)
        stmts = self.stmts()
        self.match(Tokentype.Dedent)
        return stmts
    
    def target_m(self):
        if self.match_if(Tokentype.Period):
            self.match(Tokentype.Identifier)
            self.target_m()
        elif self.match_if(Tokentype.BracketL):
            self.expr()
            self.match(Tokentype.BracketR)
            self.target_m()
        # TODO: add AST

    def target(self):
        if self.match_if(Tokentype.Identifier):
            self.target_m()
        else:
            self.cexpr()
            self.target_m()
        # TODO: add AST
    
    def asgn_stmt_m(self):
        targets = []
        if self.match_if(Tokentype.OpAssign):
            targets.append(self.target())
            targets.append(self.asgn_stmt_m())
        return targets
        
    def asgn_stmt(self):
        targets = [self.target()]
        self.match(Tokentype.OpAssign)
        expr = self.expr()
        targets.append(self.asgn_stmt_m())
        return AssignStmtNode(targets, expr)
    
    def asgn_stmts_m(self):
        asgn_stmts = [self.asgn_stmt()]
        asgn_stmts.append(self.asgn_stmts_m())
        return asgn_stmts
    
    def asgn_stmts(self):
        asgn_stmt_nodes = [self.asgn_stmt()]
        asgn_stmt_nodes.append(self.asgn_stmts_m())
        return asgn_stmt_nodes

    def si_stmt(self):
        if self.match_if(Tokentype.KwPass):
            node = PassStmtNode()
            pass
        elif self.match_if(Tokentype.KwReturn):
            if self.token.type != Tokentype.Newline:
               expr = self.expr()
            node = ReturnStmtNode(expr)
        else:
            expr = self.expr()
            # TODO: Check if node is expression or assignment
            if expr is AssignStmtNode:
                # TODO: Create assign
                ...
            node = ExprStmt(expr)
        return node


    def for_stmt(self):
        self.match(Tokentype.KwFor)
        id_node = IdentifierNode(self.token.lexeme)
        self.match(Tokentype.Identifier)
        self.match(Tokentype.OpIn)
        expr = self.expr()
        self.match(Tokentype.Colon)
        stmts = self.block()
        return ForStmtNode(id_node, expr, stmts)

    def wh_stmt(self):
        self.match(Tokentype.KwWhile)
        expr = self.expr()
        self.match(Tokentype.Colon)
        stmts = self.block()
        return WhileStmtNode(expr, stmts)

    def elif_stmt(self):
        self.match(Tokentype.KwElif)
        expr = self.expr()
        self.match(Tokentype.Colon)
        stmts = self.block()
        return (expr, stmts)

    def elif_stmts_m(self):
        elifs = []
        if self.token.type == Tokentype.KwElif:
            elifs.append(self.elif_stmts())
            elifs.append(self.elif_stmts_m())
        else:
            pass #eps
        return elifs

    def elif_stmts(self):
        elifs = []
        elifs.append(self.elif_stmt())
        elifs.append(self.elif_stmts_m())
        return elifs
    
    def if_stmt(self):
        self.match(Tokentype.KwIf)
        condition = self.expr()
        self.match(Tokentype.Colon)
        then_body, elifs = self.if_block()
        if self.match_if(Tokentype.KwElse):
            else_body = self.block()
        else_body = [] if not else_body else else_body
        return IfStmtNode(condition, then_body, elifs, else_body)

    def if_block(self):
        if_body = self.block()
        elifs = self.elif_stmts_m()
        return if_body, elifs
    
    def var_def(self):
        typed_var_node = self.typed_var()
        self.match(Tokentype.OpAssign)
        value = self.literal()
        self.match(Tokentype.Newline)
        return VarDefNode(typed_var_node, value)

    def nonloc_decl(self):
        self.match(Tokentype.KwNonLocal)
        id_node = IdentifierNode(self.token.lexeme)
        self.match(Tokentype.Identifier)
        self.match(Tokentype.Newline)
        return NonLocalDeclNode(id_node)

    def global_decl(self):
        self.match(Tokentype.KwGlobal)
        id_node = IdentifierNode(self.token.lexeme)
        self.match(Tokentype.Identifier)
        self.match(Tokentype.Newline)
        return GlobalDeclNode(id_node)

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
            node = self.global_decl()
        elif self.token.type == Tokentype.KwNonLocal:
            node = self.nonloc_decl()
        elif self.token.type == Tokentype.KwDef:
            node = self.func_def()
        else:
            node = self.var_def()
        return node
    
    def all_decls_m(self):
        decls = []
        if self.token.type in [Tokentype.KwGlobal, Tokentype.KwNonLocal, Tokentype.KwDef, Tokentype.Identifier]:
            decls.append(self.all_decl())
            decls.append(self.all_decls_m())
        else:
            pass #eps
        return decls

    def all_decls(self):
        decls = []
        decls.append(self.all_decl())
        decls.append(self.all_decls_m())
        return decls

    def func_body(self):
        decls = [Tokentype.KwGlobal, Tokentype.KwNonLocal, Tokentype.KwDef, Tokentype.Identifier]
        decl_nodes = []
        if self.token.type in decls :
            decl_nodes = self.all_decls()
        stmt_nodes = self.stmts()
        return decl_nodes, stmt_nodes  
        
    
    def typed_args(self):
        typed_args = [self.typed_var()]
        if self.match_if(Tokentype.Comma):
            typed_args.append(self.typed_args())
        return typed_args


    def func_def(self):
        self.match(Tokentype.KwDef)
        id_node = IdentifierNode(self.token.lexeme)
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
        return FuncDefNode(id_node, param_list, return_type, decls, stmts)

    def vf_def(self):
        if self.token.type == Tokentype.KwDef:
            node = self.func_def()
        else:
            node = self.var_def()
        return node

    def vf_defs_m(self):
        vf_defs = []
        if self.token.type in [Tokentype.KwDef, Tokentype.Identifier]:
            vf_defs.append(self.vf_def())
            vf_defs.append(self.vf_defs_m())
        return vf_defs
            
    def vf_defs(self):
        vf_defs = []
        vf_defs.append(self.vf_def())
        vf_defs.append(self.vf_defs_m())
        return vf_defs 
    
    def class_body(self):
        decl_nodes = []
        if self.match_if(Tokentype.KwPass):
            self.match(Tokentype.Newline)
        else:
            decl_nodes = self.vf_defs()
        return decl_nodes

    def class_def(self):
        self.match(Tokentype.KwClass)
        id_node = IdentifierNode(self.token.lexeme)
        self.match(Tokentype.Identifier)
        self.match(Tokentype.ParenthesisL)
        super_class = IdentifierNode(self.token.lexeme)
        self.match(Tokentype.Identifier)
        self.match(Tokentype.ParenthesisR)
        self.match(Tokentype.Colon)
        self.match(Tokentype.Newline)
        self.match(Tokentype.Indent)
        decls = self.class_body()
        self.match(Tokentype.Dedent)
        return ClassDefNode(id_node, super_class, decls)
    
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
        vfc_defs = []
        vfc_defs.append(self.vfc_def())
        vfc_defs.append(self.vfc_defs_m())
        return vfc_defs

    def program(self):
        stmts = []
        vfc_defs = []
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
     