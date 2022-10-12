#
# Symbol table construction visitor. Version 1.0
# Yours to implement.
#
# I've suggested some member variables to use in the constructor, but you are free to implement
# it differently, as long as the interface does not change.
#

import functools
import symbol
import astree as ast
import visitor
import symbol_table
from symbol_table import Symbol
import semantic_error
from copy import copy


class SymbolTableVisitor(visitor.Visitor):

    def __init__(self):
        # Built-in functions and their return types.
        self.built_ins = {'print': "<None>", 'len': "int", 'input': 'str'}
        self.root_sym_table = None
        self.curr_sym_table = None
        ...  # add more member variables as needed.
        pass

    def do_visit(self, node):
        if node:
            self.visit(node)

    @functools.singledispatchmethod
    def visit(self, node):
        print("Visitor support missing for", type(node))
        exit()

    @visit.register
    def _(self, node: ast.IdentifierNode):
        if node.name in self.built_ins.keys():
            ts = self.built_ins[node.name]
            s = Symbol(node.name, 0b0001, type_str=ts)
            self.curr_sym_table.add_symbol(s)
        ...

    @visit.register
    def _(self, node: ast.NoneLiteralExprNode):
        ...

    @visit.register
    def _(self, node: ast.StringLiteralExprNode):
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
    def _(self, node: ast.IndexExprNode):
        self.do_visit(node.list_expr)
        self.do_visit(node.index)

    @visit.register
    def _(self, node: ast.MemberExprNode):
        self.do_visit(node.expr_object)
        self.do_visit(node.member)

    @visit.register
    def _(self, node: ast.FunctionCallExprNode):
        self.do_visit(node.identifier)
        for a in node.args:
            self.do_visit(a)

    @visit.register
    def _(self, node: ast.MethodCallExprNode):
        self.do_visit(node.member)
        for a in node.args:
            self.do_visit(a)

    @visit.register
    def _(self, node: ast.ListExprNode):
        for e in node.elements:
            self.do_visit(e)

    @visit.register
    def _(self, node: ast.PassStmtNode):
        pass

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
    def _(self, node: ast.ForStmtNode):
        self.do_visit(node.identifier)
        self.do_visit(node.iterable)
        for s in node.body:
            self.do_visit(s)

    @visit.register
    def _(self, node: ast.ClassTypeAnnotationNode):
        pass

    @visit.register
    def _(self, node: ast.ListTypeAnnotationNode):
        self.do_visit(node.elem_type)

    @visit.register
    def _(self, node: ast.TypedVarNode):
        self.do_visit(node.identifier)
        self.do_visit(node.id_type)
        flags = 0b0011 if self.curr_sym_table.get_type() == "module" else 0b0010
        if type(node.id_type) == ast.ClassTypeAnnotationNode:
            s = Symbol(node.identifier.name, flags, type_str=node.id_type.name)
        else:
            s = Symbol(node.identifier.name, flags, type_str="[" + node.id_type.elem_type.name + "]")

        self.curr_sym_table.add_symbol(s)

    @visit.register
    def _(self, node: ast.VarDefNode):
        self.do_visit(node.var)
        self.do_visit(node.value)

    @visit.register
    def _(self, node: ast.GlobalDeclNode):
        self.do_visit(node.variable)
        s = copy(self.root_sym_table.lookup(node.variable.name))
        s.set_flags(0b0001)
        self.curr_sym_table.add_symbol(s)

    @visit.register
    def _(self, node: ast.NonLocalDeclNode):
        self.do_visit(node.variable)
        s = copy(self.curr_sym_table.get_parent().lookup(node.variable.name))
        s.set_flags(0b0000)
        self.curr_sym_table.add_symbol(s)

    @visit.register
    def _(self, node: ast.ClassDefNode):
        st = symbol_table.Class(node.name.name, symbol_table.built_ins("object"))
        parent = self.curr_sym_table
        self.curr_sym_table.add_child(st)
        self.curr_sym_table = st

        self.do_visit(node.name)
        self.do_visit(node.super_class)

        ss = Symbol(node.super_class.name, 0b0001, node.super_class.name)
        flags = 0b0011 if self.curr_sym_table.get_parent().get_type() == "module" else 0b0010
        s = Symbol(node.name.name, flags, type_str=node.name.name)
        self.curr_sym_table.get_parent().add_symbol(s)
        self.curr_sym_table.get_parent().add_symbol(ss)
        for d in node.declarations:
            self.do_visit(d)

        self.curr_sym_table = parent

    @visit.register
    def _(self, node: ast.FuncDefNode):
        if self.curr_sym_table.get_type() == "function":
            st = symbol_table.Function(node.name.name, is_nested=True)
        else:
            st = symbol_table.Function(node.name.name)
        
        parent = self.curr_sym_table
        self.curr_sym_table.add_child(st)
        self.do_visit(node.name)
        self.curr_sym_table = st

        #begin parameters
        for p in node.params:
            self.do_visit(p)
            s = self.curr_sym_table.lookup(p.identifier.name)
            s.set_flags(0b0110)
        #end parameters

        #begin return type / function identifier
        self.do_visit(node.return_type)
        rt_type = node.return_type.name if node.return_type else "<None>"
        flags = 0b0011 if self.curr_sym_table.get_parent().get_type() == "module" else 0b0010
        s = Symbol(node.name.name, flags, type_str=rt_type)
        self.curr_sym_table.get_parent().add_symbol(s)
        #end return type / function identifier

        #begin declarations
        for d in node.declarations:
            self.do_visit(d)
            #TODO: should flags be changed?
        #end declarations

        #begin statements
        for s in node.statements:
            self.do_visit(s)
        #end statements
        self.curr_sym_table = parent

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
