import functools
import ast
import visitor


class PrintVisitor(visitor.Visitor):

    def __init__(self):
        self.indent = 0

    def do_visit(self, node):
        if node:
            self.visit(node)

    def print(self, text):
        for _ in range(self.indent):
            print('   ', sep='', end='')
        print(text)

    @functools.singledispatchmethod
    def visit(self, node):
        print("Visitor support missing for", type(node))
        exit()


    @visit.register
    def _(self, node: ast.BinaryOpNode):
        self.print(node.op)
        self.indent += 1
        self.do_visit(node.lhs)
        self.do_visit(node.rhs)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.IntegerLiteral):
        self.print(node.value)

