#
# PrintVisitor version 1.05
#
import functools
import astree as ast
import visitor


class PrintVisitor(visitor.Visitor):

    def __init__(self, do_print=True):
        self.indent = 0
        self.do_print = do_print
        self.lines = []

    def clear(self):
        self.lines = []

    def do_visit(self, node):
        if node:
            self.visit(node)

    def print(self, text):
        line = []
        for _ in range(self.indent):
            line.append(' ')
        line.append(text)
        output = "".join(line)
        if self.do_print:
            print(output)
        else:
            self.lines.append(output)

    @functools.singledispatchmethod
    def visit(self, node):
        print("Visitor support missing for", type(node))
        exit()

    @visit.register
    def _(self, node: ast.IdentifierNode):
        self.print(f'(Identifier {node.name})')

    @visit.register
    def _(self, node: ast.IntegerLiteralExprNode):
        self.print(f'(Integer {node.value} t:{node.get_type_str()})')

    @visit.register
    def _(self, node: ast.BooleanLiteralExprNode):
        self.print(f'(Bool {node.value} t:{node.get_type_str()})')

    @visit.register
    def _(self, node: ast.IdentifierExprNode):
        self.print('(IdentifierExpr')
        self.indent += 1
        self.do_visit(node.identifier)
        self.indent -= 1
        self.print(f't:{node.get_type_str()})')

    @visit.register
    def _(self, node: ast.BinaryOpExprNode):
        self.print(f'(BinaryOperator {node.op}')
        self.indent += 1
        self.do_visit(node.lhs)
        self.do_visit(node.rhs)
        self.indent -= 1
        self.print(f't:{node.get_type_str()})')

    @visit.register
    def _(self, node: ast.UnaryOpExprNode):
        self.print(f'(UnaryOperator {node.op}')
        self.indent += 1
        self.do_visit(node.operand)
        self.indent -= 1
        self.print(f't:{node.get_type_str()})')

    @visit.register
    def _(self, node: ast.IfExprNode):
        self.print('(IfExpr')
        self.indent += 1
        self.do_visit(node.condition)
        self.do_visit(node.then_expr)
        self.do_visit(node.else_expr)
        self.indent -= 1
        self.print(f't:{node.get_type_str()})')

    @visit.register
    def _(self, node: ast.FunctionCallExprNode):
        self.print('(FunctionCallExpr')
        self.indent += 1
        self.do_visit(node.identifier)
        for a in node.args:
            self.do_visit(a)
        self.indent -= 1
        self.print(f't:{node.get_type_str()})')

    @visit.register
    def _(self, node: ast.ExprStmtNode):
        self.print('(ExprStmt')
        self.indent += 1
        self.do_visit(node.expr)
        self.indent -= 1
        self.print(')')

    @visit.register
    def _(self, node: ast.PassStmtNode):
        self.print('PassStmt)')

    @visit.register
    def _(self, node: ast.ReturnStmtNode):
        self.print('(ReturnStmt')
        self.indent += 1
        self.do_visit(node.expr)
        self.indent -= 1
        self.print(')')

    @visit.register
    def _(self, node: ast.AssignStmtNode):
        self.print('(AssignStmt')
        self.indent += 1
        for t in node.targets:
            self.do_visit(t)
        self.do_visit(node.expr)
        self.indent -= 1
        self.print(')')

    @visit.register
    def _(self, node: ast.IfStmtNode):
        self.print('(IfStmt')
        self.indent += 1
        self.do_visit(node.condition)
        self.print('then')
        for s in node.then_body:
            self.do_visit(s)
        for e in node.elifs:
            self.print('elif')
            self.do_visit(e[0])
            for s in e[1]:
                self.do_visit(s)
        self.print('else')
        for s in node.else_body:
            self.do_visit(s)
        self.indent -= 1
        self.print(')')

    @visit.register
    def _(self, node: ast.WhileStmtNode):
        self.print('(WhileStmt')
        self.indent += 1
        self.do_visit(node.condition)
        for s in node.body:
            self.do_visit(s)
        self.indent -= 1
        self.print(')')

    @visit.register
    def _(self, node: ast.TypeAnnotationNode):
        self.print(f'(TypeAnnotation {node.name})')

    @visit.register
    def _(self, node: ast.TypedVarNode):
        self.print('(TypedVar')
        self.indent += 1
        self.do_visit(node.identifier)
        self.do_visit(node.id_type)
        self.indent -= 1
        self.print(')')

    @visit.register
    def _(self, node: ast.VarDefNode):
        self.print('(VarDef')
        self.indent += 1
        self.do_visit(node.var)
        self.do_visit(node.value)
        self.indent -= 1
        self.print(')')

    @visit.register
    def _(self, node: ast.FuncDefNode):
        self.print('(FuncDef')
        self.indent += 1
        self.do_visit(node.name)
        for p in node.params:
            self.do_visit(p)
        self.do_visit(node.return_type)
        for d in node.declarations:
            self.do_visit(d)
        for s in node.statements:
            self.do_visit(s)
        self.indent -= 1
        self.print(')')

    @visit.register
    def _(self, node: ast.ProgramNode):
        self.print('(Program')
        self.indent += 1
        for d in node.declarations:
            self.do_visit(d)
        for s in node.statements:
            self.do_visit(s)
        self.indent -= 1
        self.print(')')
