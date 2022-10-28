#
# This visitor builds the symbol table.
#
import functools
import astree as ast
import visitor
import symbol_table
from symbol_table import Symbol
import error


class SymbolTableVisitor(visitor.Visitor):

    def __init__(self):
        # Built-in functions and their return types.
        self.built_ins = {'print': "<None>", 'len': "int", 'input': 'str', 'object': 'object'}
        self.root_sym_table = None
        self.curr_sym_table = None
        self.in_parameters: bool = False

    def is_built_in(self, name: str):
        return name in self.built_ins.keys()

    def built_in_type(self, name: str):
        return self.built_ins[name]

    def lookup(self, name: str):
        sym_table = self.curr_sym_table
        while sym_table is not None:
            symbol = sym_table.lookup(name)
            if symbol is not None:
                return symbol
            sym_table = sym_table.get_parent()
        if self.is_built_in(name):
            symbol = symbol_table.Symbol(name, Symbol.Is.Global, self.built_in_type(name))
            self.curr_sym_table.add_symbol(symbol)
            return symbol
        return None

    def do_visit(self, node):
        if node:
            self.visit(node)

    @functools.singledispatchmethod
    def visit(self, node):
        print("Visitor support missing for", type(node))
        exit()

    @visit.register
    def _(self, node: ast.IdentifierNode):
        # self.print(f'(Identifier {node.name})')
        ...

    @visit.register
    def _(self, node: ast.IntegerLiteralExprNode):
        ...

    @visit.register
    def _(self, node: ast.BooleanLiteralExprNode):
        ...

    @visit.register
    def _(self, node: ast.IdentifierExprNode):
        self.do_visit(node.identifier)
        symbol = self.curr_sym_table.lookup(node.identifier.name)
        if symbol is None:
            # Implicit local or global variable.
            symbol = self.lookup(node.identifier.name)
            if symbol:
                flags = Symbol.Is.ReadOnly
                flags = Symbol.Is.Global | flags if symbol.is_global() else flags
                self.curr_sym_table.add_symbol(symbol_table.Symbol(node.identifier.name, flags, symbol.get_type_str()))
            else:
                # error undefined identifier.
                raise error.UndefinedIdentifierException(node.identifier.name,
                                                         self.curr_sym_table.get_name())

    @visit.register
    def _(self, node: ast.BinaryOpExprNode):
        self.do_visit(node.lhs)
        self.do_visit(node.rhs)

    @visit.register
    def _(self, node: ast.UnaryOpExprNode):
        self.do_visit(node.operand)

    @visit.register
    def _(self, node: ast.IfExprNode):
        self.do_visit(node.condition)
        self.do_visit(node.then_expr)
        self.do_visit(node.else_expr)

    @visit.register
    def _(self, node: ast.FunctionCallExprNode):
        symbol = self.curr_sym_table.lookup(node.identifier.name)
        if symbol is None:
            # Check enclosing scopes.
            symbol = self.lookup(node.identifier.name)
            if symbol:
                flags = Symbol.Is.Global if symbol.is_global() else 0
                self.curr_sym_table.add_symbol(symbol_table.Symbol(node.identifier.name, flags, symbol.get_type_str()))
            else:
                # error undefined identifier.
                raise error.UndefinedIdentifierException(node.identifier.name, self.curr_sym_table.get_name())
        for a in node.args:
            self.do_visit(a)

    @visit.register
    def _(self, node: ast.ExprStmtNode):
        self.do_visit(node.expr)

    @visit.register
    def _(self, node: ast.PassStmtNode):
        ...

    @visit.register
    def _(self, node: ast.ReturnStmtNode):
        self.do_visit(node.expr)

    @visit.register
    def _(self, node: ast.AssignStmtNode):
        for t in node.targets:
            self.do_visit(t)
        self.do_visit(node.expr)

    @visit.register
    def _(self, node: ast.IfStmtNode):
        self.do_visit(node.condition)
        for s in node.then_body:
            self.do_visit(s)
        for e in node.elifs:
            self.do_visit(e[0])
            for s in e[1]:
                self.do_visit(s)
        for s in node.else_body:
            self.do_visit(s)

    @visit.register
    def _(self, node: ast.WhileStmtNode):
        self.do_visit(node.condition)
        for s in node.body:
            self.do_visit(s)

    @visit.register
    def _(self, node: ast.TypeAnnotationNode):
        ...

    @visit.register
    def _(self, node: ast.TypedVarNode):
        self.do_visit(node.identifier)
        self.do_visit(node.id_type)
        flags = Symbol.Is.Local
        flags = flags | Symbol.Is.Global if self.curr_sym_table.get_type() == 'module' else flags
        flags = flags | Symbol.Is.Parameter if self.in_parameters else flags
        type_str = node.id_type.to_str()
        if self.curr_sym_table.lookup(node.identifier.name):
            raise error.RedefinedIdentifierException(node.identifier.name, self.curr_sym_table.get_name())
        self.curr_sym_table.add_symbol(symbol_table.Symbol(node.identifier.name, flags, type_str))

    @visit.register
    def _(self, node: ast.VarDefNode):
        self.do_visit(node.var)
        self.do_visit(node.value)

    @visit.register
    def _(self, node: ast.FuncDefNode):
        self.do_visit(node.name)
        if self.curr_sym_table.lookup(node.name.name):
            raise error.RedefinedIdentifierException(node.name.name, self.curr_sym_table.get_name())
        flags = Symbol.Is.Local | Symbol.Is.Global if self.curr_sym_table.get_type() == 'module' else Symbol.Is.Local
        type_str = node.return_type.to_str() if node.return_type is not None else '<None>'
        self.curr_sym_table.add_symbol(symbol_table.Symbol(node.name.name, flags, type_str))
        sym_table = symbol_table.Function(node.name.name, self.curr_sym_table.get_type() == 'function')
        self.curr_sym_table.add_child(sym_table)
        self.curr_sym_table = sym_table
        self.in_parameters = True
        for p in node.params:
            self.do_visit(p)
        self.in_parameters = False
        self.do_visit(node.return_type)
        for d in node.declarations:
            self.do_visit(d)
        for s in node.statements:
            self.do_visit(s)
        self.curr_sym_table = self.curr_sym_table.get_parent()

    @visit.register
    def _(self, node: ast.ProgramNode):
        self.root_sym_table = symbol_table.SymbolTable('top')
        self.curr_sym_table = self.root_sym_table
        for d in node.declarations:
            self.do_visit(d)
        for s in node.statements:
            self.do_visit(s)
        self.curr_sym_table = self.root_sym_table

    def get_symbol_table(self) -> symbol_table.SymbolTable:
        return self.root_sym_table
