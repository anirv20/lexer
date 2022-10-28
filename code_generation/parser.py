from lexer import Lexer, Tokentype
import error
import astree as ast


class Parser:

    def __init__(self, f):
        self.lexer = Lexer(f)
        self.token = self.lexer.next()
        self.token_peek = None

    # Helper function.
    def match(self, ttype):
        if self.token.type == ttype:
            if self.token_peek is None:
                self.token = self.lexer.next()
            else:
                self.token = self.token_peek
                self.token_peek = None
        else:
            text = "Syntax error: expected {:s} but got {:s} ({:s}).".format(
                ttype, self.token.type, self.token.lexeme)
            raise error.SyntaxErrorException(text, self.token.location)

    # Helper function
    def match_if(self, ttype):
        if self.token.type == ttype:
            self.match(ttype)
            return True
        return False

    # Helper function
    def peek(self):
        if self.token_peek is None:
            self.token_peek = self.lexer.next()
        return self.token_peek

    def parse(self):
        node = self.program()
        self.match(Tokentype.EOI)
        return node

    def program(self):
        declarations = []
        while self.token.type == Tokentype.KwDef:
            node = self.func_def()
            declarations.append(node)
        statements = []
        while self.token.type != Tokentype.EOI:
            node = self.statement()
            statements.append(node)
        return ast.ProgramNode(declarations, statements)

    def identifier(self):
        lexeme = self.token.lexeme
        self.match(Tokentype.Identifier)
        return ast.IdentifierNode(lexeme)

    def func_def(self):
        self.match(Tokentype.KwDef)
        name = self.identifier()
        self.match(Tokentype.ParenthesisL)
        params = []
        if self.token.type != Tokentype.ParenthesisR:
            params.append(self.typed_var())
            while self.match_if(Tokentype.Comma):
                params.append(self.typed_var())
        self.match(Tokentype.ParenthesisR)
        return_type = None
        if self.match_if(Tokentype.Arrow):
            return_type = self.type()
        self.match(Tokentype.Colon)
        self.match(Tokentype.Newline)
        self.match(Tokentype.Indent)
        declarations = []
        while self.token.type == Tokentype.Identifier and self.peek().type == Tokentype.Colon:
            node = self.var_def()
            declarations.append(node)
        statements = [self.statement()]
        while self.token.type != Tokentype.Dedent:
            statements.append(self.statement())
        self.match(Tokentype.Dedent)
        return ast.FuncDefNode(name, params, return_type, declarations, statements)

    def typed_var(self):
        identifier = self.identifier()
        self.match(Tokentype.Colon)
        id_type = self.type()
        return ast.TypedVarNode(identifier, id_type)

    def type(self):
        node = ast.TypeAnnotationNode(self.token.lexeme)
        self.match(Tokentype.Identifier)
        return node

    def var_def(self):
        var = self.typed_var()
        self.match(Tokentype.OpAssign)
        literal = self.literal()
        self.match(Tokentype.Newline)
        return ast.VarDefNode(var, literal)

    def statement(self):
        if self.token.type == Tokentype.KwIf:
            self.match(Tokentype.KwIf)
            condition = self.expr()
            self.match(Tokentype.Colon)
            then_body = self.block()
            elifs = []
            while self.match_if(Tokentype.KwElif):
                e_cond = self.expr()
                self.match(Tokentype.Colon)
                ebody = self.block()
                elifs.append((e_cond, ebody))
            if self.match_if(Tokentype.KwElse):
                self.match(Tokentype.Colon)
                else_body = self.block()
            else:
                else_body = []
            node = ast.IfStmtNode(condition, then_body, elifs, else_body)
        elif self.token.type == Tokentype.KwWhile:
            self.match(Tokentype.KwWhile)
            condition = self.expr()
            self.match(Tokentype.Colon)
            body = self.block()
            node = ast.WhileStmtNode(condition, body)
        else:
            node = self.simple_stmt()
            self.match(Tokentype.Newline)
        return node

    def simple_stmt(self):
        if self.match_if(Tokentype.KwPass):
            node = ast.PassStmtNode()
        elif self.match_if(Tokentype.KwReturn):
            if self.token.type != Tokentype.Newline:
                expr = self.expr()
            else:
                expr = None
            node = ast.ReturnStmtNode(expr)
        else:
            node = self.expr()
            targets = []
            while self.match_if(Tokentype.OpAssign):
                # Must limit the type of expr allowed on the left-hand-side of an assignment.
                if not isinstance(node, ast.IdentifierExprNode):
                    text = "Syntax error: invalid left-hand-side in assignment"
                    raise error.SyntaxErrorException(text, self.token.location)
                targets.append(node)
                node = self.expr()
            if targets:
                node = ast.AssignStmtNode(targets, node)
            else:
                node = ast.ExprStmtNode(node)
        return node

    def block(self):
        self.match(Tokentype.Newline)
        self.match(Tokentype.Indent)
        statements = [self.statement()]
        while self.token.type != Tokentype.Dedent:
            statements.append(self.statement())
        self.match(Tokentype.Dedent)
        return statements

    def literal(self):
        if self.match_if(Tokentype.BoolTrueLiteral):
            node = ast.BooleanLiteralExprNode(True)
        elif self.match_if(Tokentype.BoolFalseLiteral):
            node = ast.BooleanLiteralExprNode(False)
        else:
            node = ast.IntegerLiteralExprNode(int(self.token.lexeme))
            self.match(Tokentype.IntegerLiteral)
        return node

    def expr(self):
        expr = self.or_expr()
        if self.match_if(Tokentype.KwIf):
            condition = self.expr()
            self.match(Tokentype.KwElse)
            else_expr = self.expr()
            expr = ast.IfExprNode(condition, expr, else_expr)
        return expr

    def or_expr(self):
        expr = self.and_expr()
        while self.match_if(Tokentype.OpOr):
            rhs = self.and_expr()
            expr = ast.BinaryOpExprNode(ast.Operator.Or, expr, rhs)
        return expr

    def and_expr(self):
        expr = self.not_expr()
        while self.match_if(Tokentype.OpAnd):
            rhs = self.not_expr()
            expr = ast.BinaryOpExprNode(ast.Operator.And, expr, rhs)
        return expr

    def not_expr(self):
        if self.match_if(Tokentype.OpNot):
            operand = self.not_expr()
            node = ast.UnaryOpExprNode(ast.Operator.Not, operand)
        else:
            node = self.cexpr()
        return node

    def cexpr(self):
        ops = {Tokentype.OpEq: ast.Operator.Eq,
               Tokentype.OpNotEq: ast.Operator.NotEq,
               Tokentype.OpGtEq: ast.Operator.GtEq,
               Tokentype.OpLtEq: ast.Operator.LtEq,
               Tokentype.OpLt: ast.Operator.Lt,
               Tokentype.OpGt: ast.Operator.Gt}
        node = self.aexpr()
        if self.token.type in ops.keys():
            operator = ops[self.token.type]
            self.match(self.token.type)
            rhs = self.aexpr()
            node = ast.BinaryOpExprNode(operator, node, rhs)
        return node

    def aexpr(self):
        ops = {Tokentype.OpPlus: ast.Operator.Plus,
               Tokentype.OpMinus: ast.Operator.Minus}
        node = self.mexpr()
        while self.token.type in ops.keys():
            operator = ops[self.token.type]
            self.match(self.token.type)
            rhs = self.mexpr()
            node = ast.BinaryOpExprNode(operator, node, rhs)
        return node

    def mexpr(self):
        ops = {Tokentype.OpMultiply: ast.Operator.Mult,
               Tokentype.OpIntDivide: ast.Operator.IntDivide,
               Tokentype.OpModulus: ast.Operator.Modulus}
        node = self.nexpr()
        while self.token.type in ops.keys():
            operator = ops[self.token.type]
            self.match(self.token.type)
            rhs = self.nexpr()
            node = ast.BinaryOpExprNode(operator, node, rhs)
        return node

    def nexpr(self):
        if self.match_if(Tokentype.OpMinus):
            operand = self.nexpr()
            node = ast.UnaryOpExprNode(ast.Operator.Minus, operand)
        else:
            node = self.fexpr()
        return node

    def arguments(self):
        self.match(Tokentype.ParenthesisL)
        args = []
        if self.token.type != Tokentype.ParenthesisR:
            args.append(self.expr())
            while self.match_if(Tokentype.Comma):
                args.append(self.expr())
        self.match(Tokentype.ParenthesisR)
        return args

    def fexpr(self):
        if self.match_if(Tokentype.ParenthesisL):
            node = self.expr()
            self.match(Tokentype.ParenthesisR)
        elif self.token.type == Tokentype.Identifier:
            identifier = self.identifier()
            if self.token.type == Tokentype.ParenthesisL:
                arguments = self.arguments()
                node = ast.FunctionCallExprNode(identifier, arguments)
            else:
                node = ast.IdentifierExprNode(identifier)
        else:
            node = self.literal()
        return node
