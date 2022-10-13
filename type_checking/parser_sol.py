from ast import NotEq
from lib2to3.pgen2.tokenize import TokenError
import numbers
from lexer import Lexer, Tokentype, SyntaxErrorException
from astree import *

class Parser:

    def __init__(self, f):
        self.lexer = Lexer(f)
        self.token = self.lexer.next()
        #print(self.token)
        self.token_peek = None
        self.indentation = 0
        self.num_space = 2

    # Helper function.
    def match(self, type):
        if self.token.type == type:
            #print(self.token)
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
                args = []
                if self.token.type != Tokentype.ParenthesisR:
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
                args = []
            else:
                args = self.args()
            id_node = IdentifierNode(lexeme)
            node = FunctionCallExprNode(id_node, args)
        return node

    def mi_expr_m(self):
        if self.match_if(Tokentype.Period):
            expr = self.i_or_f()
            member = self.mi_expr_m()
            if member:
                return MemberExprNode(expr, member)
            else:
                return expr
        elif self.match_if(Tokentype.BracketL):
            index = self.expr()
            self.match(Tokentype.BracketR)
            li_expr = self.mi_expr_m()
            return IndexExprNode(li_expr, index)
        else:
            pass #eps
        

    def mi_expr(self):
        expr = self.fexpr()
        print(expr)
        if self.token.type == Tokentype.Period or self.token_peek  == Tokentype.BracketL:
            member = self.mi_expr_m()
            return MemberExprNode(expr, member)
        return expr

    def uexpr(self):
        if self.match_if(Tokentype.OpMinus):
            node = self.uexpr()
            node = UnaryOpExprNode(Operator.Minus, node)
        else:
            node = self.mi_expr()
        return node
            
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
        node = self.uexpr()
        ops = {
            Tokentype.OpMultiply: Operator.Mult,
            Tokentype.OpModulus: Operator.Modulus,
            Tokentype.OpIntDivide: Operator.IntDivide
        }
        if self.token.type in ops.keys():
            op = ops[self.token.type]
            rhs = self.mexpr_m()
            node = BinaryOpExprNode(op, node, rhs)
        return node

    def add_op(self):
        if self.match_if(Tokentype.OpPlus):
            return Operator.Plus
        elif self.match_if(Tokentype.OpMinus):
            return Operator.Minus

    def aexpr_m(self):
        if self.token.type in [Tokentype.OpPlus, Tokentype.OpMinus]:
            op = self.add_op()
            lhs = self.mexpr()
            rhs = self.aexpr_m()
            node = BinaryOpExprNode(op, lhs, rhs)
            return node


    def aexpr(self):
        node = self.mexpr()
        ops = {
            Tokentype.OpPlus: Operator.Plus,
            Tokentype.OpMinus: Operator.Minus
        }
        if self.token.type in ops.keys():
            op = ops[self.token.type]
            rhs = self.aexpr_m()
            node = BinaryOpExprNode(op, node, rhs)
        return node

    def rel_op(self):
        if self.match_if(Tokentype.OpEq):
            return Operator.Eq
        elif self.match_if(Tokentype.OpNotEq):
            return Operator.NotEq
        elif self.match_if(Tokentype.OpGt):
            return Operator.Gt
        elif self.match_if(Tokentype.OpLt):
            return Operator.Lt
        elif self.match_if(Tokentype.OpLtEq):
            return Operator.LtEq
        elif self.match_if(Tokentype.OpGtEq):
            return Operator.GtEq
        elif self.match_if(Tokentype.OpIs):
            return Operator.Is


    def cexpr(self):
        lhs = self.aexpr()
        node = lhs
        if self.token.type in [Tokentype.OpEq, Tokentype.OpNotEq, Tokentype.OpGt, Tokentype.OpLt, Tokentype.OpLtEq, Tokentype.OpGtEq, Tokentype.OpIs]:
            op = self.rel_op()
            rhs = self.aexpr()
            node = BinaryOpExprNode(op, lhs, rhs)
        return node
    
    def not_expr(self):
        if self.match_if(Tokentype.OpNot):
            op = Operator.Not
            operand = self.cexpr()
            return UnaryOpExprNode(op, operand)
        return self.cexpr()

    def and_expr_m(self):
        if self.match_if(Tokentype.OpAnd):
            rhs = self.not_expr()
            return rhs
        
    def and_expr(self):
        lhs = self.not_expr()
        rhs = self.and_expr_m()
        if rhs:
            return BinaryOpExprNode(Operator.And, lhs, rhs)
        else:
            return lhs


    def or_expr_m(self):
        if self.match_if(Tokentype.OpOr):
            lhs = self.and_expr()
            rhs = self.or_expr_m()
            return BinaryOpExprNode(Operator.Or, lhs, rhs)
    
    def or_expr(self):
        lhs = self.and_expr()
        rhs = self.or_expr_m()
        if rhs:
            return BinaryOpExprNode(Operator.Or, lhs, rhs)
        else:
            return lhs

    def expr(self):
        lhs = self.or_expr()
        node = lhs
        if self.match_if(Tokentype.KwIf):
            condition = self.expr()
            self.match(Tokentype.KwElse)
            else_expr = self.expr()
            node = IfExprNode(condition, lhs, else_expr)
        return node
            
    def lexpr(self):
        lexeme = self.token.lexeme
        if self.match_if(Tokentype.BracketL):
            args = self.args()
            self.match(Tokentype.BracketR)
            node = ListExprNode(args)
        elif self.match_if(Tokentype.Identifier):
            node = IdentifierExprNode(IdentifierNode(lexeme))
        else:
            node = self.literal()
        return node
    
    def pexpr(self):
        if self.match_if(Tokentype.ParenthesisL):
            if self.token.type != Tokentype.ParenthesisR:
                node = self.expr()
            self.match(Tokentype.ParenthesisR)
        else:
            node = self.lexpr()
        return node

    def args(self):
        exprs = []
        exprs.append(self.expr())
        if self.match_if(Tokentype.Comma):
            exprs.extend(self.args())
        return exprs

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
            stmts.extend(self.stmts_m())
        else:
            pass
        return stmts

    def stmts(self):
        stmt_nodes = []
        stmt_nodes.append(self.stmt())
        stmt_nodes.extend(self.stmts_m())
        return stmt_nodes

    def block(self):
        self.match(Tokentype.Newline)
        self.match(Tokentype.Indent)
        stmts = self.stmts()
        self.match(Tokentype.Dedent)
        return stmts
    
    def target_m(self):
        if self.match_if(Tokentype.Period):
            lexeme = self.token.lexeme
            id_node = IdentifierNode(lexeme)
            self.match(Tokentype.Identifier)
            expr_object = self.target_m()
            node = MemberExprNode(expr_object, id_node)
        elif self.match_if(Tokentype.BracketL):
            index = self.expr()
            self.match(Tokentype.BracketR)
            expr = self.target_m()
            node = IndexExprNode(expr, index)
        return node

    def target(self):
        lexeme = self.token.lexeme
        if self.match_if(Tokentype.Identifier):
            member = self.target_m()
            expr_object = IdentifierNode(lexeme)
            node = MemberExprNode(expr_object, member)
        else:
            expr = self.cexpr()
            member = self.target_m()
            node = MemberExprNode(expr, member)
        return node
    
    def asgn_stmt_m(self):
        targets = []
        if self.match_if(Tokentype.OpAssign):
            targets.extend(self.target())
            targets.extend(self.asgn_stmt_m())
        return targets
        
    def asgn_stmt(self, target=None):
        if not target:
            targets = [self.target()]
        else:
            targets = [target]
        self.match(Tokentype.OpAssign)
        expr = self.expr()
        targets.extend(self.asgn_stmt_m())
        return AssignStmtNode(targets, expr)
    
    def asgn_stmts_m(self):
        asgn_stmts = [self.asgn_stmt()]
        asgn_stmts.extend(self.asgn_stmts_m())
        return asgn_stmts
    
    def asgn_stmts(self):
        asgn_stmt_nodes = [self.asgn_stmt()]
        asgn_stmt_nodes.extend(self.asgn_stmts_m())
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
            if isinstance(expr, ExprNode):
                if self.token.type == Tokentype.OpAssign:
                    node = self.asgn_stmt(target=expr)
                else:
                    node = expr
            else:
                raise SyntaxErrorException("Invalid expression", self.token.location)
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
            elifs.extend(self.elif_stmts())
            elifs.extend(self.elif_stmts_m())
        else:
            pass #eps
        return elifs

    def elif_stmts(self):
        elifs = []
        elifs.append(self.elif_stmt())
        elifs.extend(self.elif_stmts_m())
        return elifs
    
    def if_stmt(self):
        self.match(Tokentype.KwIf)
        condition = self.expr()
        self.match(Tokentype.Colon)
        then_body, elifs = self.if_block()
        else_body = []
        if self.match_if(Tokentype.KwElse):
            else_body = self.block()
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
            if self.peek().type not in [Tokentype.ParenthesisL, Tokentype.OpAssign]:
                decls.append(self.all_decl())
                decls.extend(self.all_decls_m())
        else:
            pass #eps
        return decls

    def all_decls(self):
        decls = []
        all_decl = self.all_decl()
        if all_decl:
            decls.append(all_decl)        
        decls.extend(self.all_decls_m())
        return decls

    def func_body(self):
        decls = [Tokentype.KwGlobal, Tokentype.KwNonLocal, Tokentype.KwDef, Tokentype.Identifier]
        decl_nodes = []
        if self.token.type in decls :
            if self.peek().type not in [Tokentype.ParenthesisL, Tokentype.OpAssign]:
                decl_nodes = self.all_decls()
        stmt_nodes = self.stmts()
        return decl_nodes, stmt_nodes  
        
    
    def typed_args(self):
        typed_args = [self.typed_var()]
        if self.match_if(Tokentype.Comma):
            typed_args.extend(self.typed_args())
        return typed_args


    def func_def(self):
        self.match(Tokentype.KwDef)
        id_node = IdentifierNode(self.token.lexeme)
        self.match(Tokentype.Identifier)
        self.match(Tokentype.ParenthesisL)
        param_list = []
        if self.match_if(Tokentype.ParenthesisR):
            pass
        else:
            param_list = self.typed_args()
            self.match(Tokentype.ParenthesisR)
        #param_list = [] if not param_list else param_list
        return_type = None
        if self.match_if(Tokentype.Arrow):
            return_type = self.type()
        self.match(Tokentype.Colon)
        self.match(Tokentype.Newline)
        self.match(Tokentype.Indent)
        decls, stmts = self.func_body()
        self.match(Tokentype.Dedent)
        #if return_type:
        return FuncDefNode(id_node, param_list, return_type, decls, stmts)
        #else:
        #    return FuncDefNode(name = id_node, params = param_list, return_typedeclarations = decls, statements = stmts)

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
            vf_defs.extend(self.vf_defs_m())
        return vf_defs
            
    def vf_defs(self):
        vf_defs = []
        vf_defs.append(self.vf_def())
        vf_defs.extend(self.vf_defs_m())
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
        nodes = []
        if self.token.type in [Tokentype.KwDef, Tokentype.KwClass]:
            nodes.append(self.vfc_def())
            nodes.extend(self.vfc_defs_m())
        elif self.token.type == Tokentype.Identifier and self.peek().type == Tokentype.Colon:
            nodes.append(self.vfc_def())
            nodes.extend(self.vfc_defs_m())
        else:
            pass #eps
        return nodes

    def vfc_defs(self):
        vfc_defs = []
        vfc_defs.append(self.vfc_def())
        vfc_defs.extend(self.vfc_defs_m())
        return vfc_defs

    def program(self):
        stmts = []
        vfc_defs = []
        if self.token.type in [Tokentype.KwClass, Tokentype.KwDef, Tokentype.Identifier]:
            vfc_defs = self.vfc_defs()
            if self.token.type not in [Tokentype.KwClass, Tokentype.KwDef]: # check if stmt?
                if self.token.type == Tokentype.Identifier and self.peek().type != Tokentype.Colon:
                    if self.match_if(Tokentype.EOI):
                        pass
                    else:
                        stmts = self.stmts()
        elif self.match_if(Tokentype.EOI):
            pass
        else:
            stmts = self.stmts()
        return ProgramNode(vfc_defs, stmts)
     