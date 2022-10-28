#
# Type visitor. Version 1.2
#
import functools
import astree as ast
from astree import Operator
import visitor
import error
import symbol_table
from symbol_table import Symbol
import type_env


class Signature:
    """
    Helps with working with method and function signatures.
    """
    def __init__(self, name: str, args_type: [str], return_type=''):
        self.name = name
        self.args_type = args_type
        self.return_type = return_type  # only important for method_comparability (when overriding)

    def __str__(self):
        return self.name + '(' + ",".join(self.args_type) + ')->' + self.return_type

    def same(self, other: "Signature") -> bool:
        """
        Returns True if the two signatures are exactly the same, otherwise False.
        """
        if self.name != other.name:
            return False
        if len(self.args_type) != len(other.args_type):
            return False
        for i in range(len(self.args_type)):
            if self.args_type[i] != other.args_type[i]:
                return False
        if self.return_type != other.return_type:
            return False
        return True

    def method_compatible(self, other: "Signature", t_env: type_env.TypeEnvironment) -> bool:
        """
        Returns True if the two signatures are exactly the same, except possibly in the first parameter p, where
        self's p may be a subtype of other's p, otherwise False.
        """
        if self.name != other.name:
            return False
        if len(self.args_type) != len(other.args_type):
            return False
        for i in range(len(self.args_type)):
            if self.args_type[i] != other.args_type[i]:
                if i > 0 or not t_env.is_subtype_of(self.args_type[i], other.args_type[i]):
                    return False
        if self.return_type != other.return_type:
            return False
        return True

    def call_compatible(self, other: "Signature", t_env: type_env.TypeEnvironment) -> bool:
        """
        Returns True if the names match and other's signature arguments are assignment compatible with self's.
        """
        if self.name != other.name:
            return False
        if len(self.args_type) != len(other.args_type):
            return False
        for i in range(len(self.args_type)):
            if not t_env.is_assign_comp(other.args_type[i], self.args_type[i]):
                return False
        # Note, return_type is not part of call comparability.
        return True


class TypeVisitor(visitor.Visitor):

    def __init__(self, t_env: type_env.TypeEnvironment):
        self.t_env = t_env
        self.upd_sym_table()

    def upd_sym_table(self):
        # We update the provided symbol-table with the built-in entities (thus no need to handle them specifically).
        st = self.t_env.get_symbol_table()
        # The 'print' function.
        f_st = symbol_table.Function('print')
        f_st.add_symbol(symbol_table.Symbol('val', Symbol.Is.Parameter, 'object'))
        st.add_symbol(symbol_table.Symbol('print', Symbol.Is.Global, 'int'))
        st.add_child(f_st)
        # The 'input' function.
        f_st = symbol_table.Function('input')
        st.add_symbol(symbol_table.Symbol('input', Symbol.Is.Global, 'str'))
        st.add_child(f_st)
        # The 'len' function.
        f_st = symbol_table.Function('len')
        f_st.add_symbol(symbol_table.Symbol('val', Symbol.Is.Parameter, 'object'))
        st.add_symbol(symbol_table.Symbol('len', Symbol.Is.Global, 'int'))
        st.add_child(f_st)
        # The 'object' class with constructor.
        c_st = symbol_table.Class('object', '')
        f_st = symbol_table.Function('__init__')
        f_st.add_symbol(symbol_table.Symbol('self', Symbol.Is.Parameter, 'object'))
        c_st.add_symbol(symbol_table.Symbol('__init__', Symbol.Is.Local, '<None>'))
        c_st.add_child(f_st)
        st.add_child(c_st)

    def invalid_use_error(self, node: ast.Node, text: str):
        raise error.InvalidUseException(text, self.t_env.get_scope_symbol_table().get_name(), node)

    def type_error(self, node: ast.Node, type_str_1: str, type_str_2: str):
        raise error.TypeException(type_str_1, type_str_2, self.t_env.get_scope_symbol_table().get_name(), node)

    def attribute_error(self, node: ast.Node, type_str: str, attribute_str: str):
        raise error.AttributeException(type_str, attribute_str,
                                       self.t_env.get_scope_symbol_table().get_name(), node)

    @staticmethod
    def get_signature(fst: symbol_table.Function) -> Signature:
        """
        Constructs and returns the signature of a function/method from its symbol-table entry.
        """
        args_type = [fst.lookup(p).get_type_str() for p in fst.get_parameters()]
        return_type = fst.get_parent().lookup(fst.get_name()).get_type_str()
        return Signature(fst.get_name(), args_type, return_type)

    def do_visit(self, node):
        if node:
            self.visit(node)

    @functools.singledispatchmethod
    def visit(self, node):
        print("Visitor support missing for", type(node))
        exit()

    @visit.register
    def _(self, node: ast.IdentifierNode):
        pass

    @visit.register
    def _(self, node: ast.IntegerLiteralExprNode):
        node.set_type_str('int')

    @visit.register
    def _(self, node: ast.BooleanLiteralExprNode):
        node.set_type_str('bool')

    @visit.register
    def _(self, node: ast.IdentifierExprNode):
        self.do_visit(node.identifier)
        # Look up the type of the identifier in the current symbol-table scope.
        symbol = self.t_env.get_scope_symbol_table().lookup(node.identifier.name)
        assert symbol, f"Should not happen, identifier {node.identifier.name} not in scope or missing in symbol table."
        if symbol_table.symbol_decl_type(self.t_env.get_scope_symbol_table(), node.identifier.name) != \
                symbol_table.DeclType.Variable:
            self.type_error(node, node.identifier.name, 'expected variable')
        node.set_type_str(symbol.get_type_str())

    @visit.register
    def _(self, node: ast.BinaryOpExprNode):
        self.do_visit(node.lhs)
        self.do_visit(node.rhs)
        ops_int_arth = [Operator.Minus, Operator.Plus, Operator.Modulus, Operator.IntDivide, Operator.Mult]
        ops_int_compare = [Operator.Lt, Operator.LtEq, Operator.Eq, Operator.NotEq, Operator.GtEq, Operator.Gt]
        ops_str_compare = [Operator.Eq, Operator.NotEq]
        ops_bool = [Operator.Eq, Operator.NotEq, Operator.And, Operator.Or]
        base_types = ['int', 'str', 'bool']
        if node.op in ops_int_arth and node.lhs.get_type_str() == 'int' and node.rhs.get_type_str() == 'int':
            node.set_type_str('int')
        elif node.op in ops_int_compare and node.lhs.get_type_str() == 'int' and node.rhs.get_type_str() == 'int':
            node.set_type_str('bool')
        elif node.op in ops_str_compare and node.lhs.get_type_str() == 'str' and node.rhs.get_type_str() == 'str':
            node.set_type_str('bool')
        elif node.op in ops_bool and node.lhs.get_type_str() == 'bool' and node.rhs.get_type_str() == 'bool':
            node.set_type_str('bool')
        elif node.op == Operator.Plus and node.lhs.get_type_str() == 'str' and node.rhs.get_type_str() == 'str':
            node.set_type_str('str')
        elif node.op == Operator.Plus and self.t_env.is_list_type(node.lhs.get_type_str()) and \
                self.t_env.is_list_type(node.rhs.get_type_str()):
            t1 = self.t_env.list_elem_type(node.lhs.get_type_str())
            t2 = self.t_env.list_elem_type(node.rhs.get_type_str())
            node.set_type_str(self.t_env.join(t1, t2))
        elif node.op == Operator.Is and node.lhs.get_type_str() not in base_types and \
                node.lhs.get_type_str() not in base_types:
            node.set_type_str('bool')
        else:
            self.type_error(node, node.lhs.get_type_str(), node.rhs.get_type_str())

    def lookup_member_typestr(self, name: str, name_class: str):
        for st in self.t_env.get_symbol_table().get_children():
            if st.get_type() == 'class' and st.get_name() == name_class:
                if name in st.get_identifiers():
                    return st.lookup(name).get_type_str()
        return ''

    @visit.register
    def _(self, node: ast.FunctionCallExprNode):
        self.do_visit(node.identifier)
        args_type = []
        for a in node.args:
            self.do_visit(a)
            args_type.append(a.get_type_str())
        signature = Signature(node.identifier.name, args_type)
        symbol = self.t_env.get_scope_symbol_table().lookup(node.identifier.name)
        assert symbol, f"Should not happen, identifier {node.identifier.name} not in scope or missing in symbol table."
        if symbol_table.symbol_decl_type(self.t_env.get_scope_symbol_table(), node.identifier.name) == \
                symbol_table.DeclType.Variable:
            self.type_error(node, node.identifier.name, 'expected function/class constructor')
        node.set_type_str(symbol.get_type_str())
        # Look function up in current and all enclosing scopes and make sure signature matches function definition.
        scope_st = self.t_env.get_scope_symbol_table()
        found = False
        while scope_st and not found:
            for st in scope_st.get_children():
                if st.get_name() == node.identifier.name:
                    if st.get_type() == 'function':
                        signature_defined = self.get_signature(st)
                    else:
                        # A class constructor. They are not allowed to have arguments in ChocoPy.
                        signature_defined = Signature(st.get_name(), [])
                    if not signature_defined.call_compatible(signature, self.t_env):
                        self.type_error(node, str(signature), str(signature_defined))
                    found = True
                    break
            scope_st = scope_st.get_parent()
        assert found, f"Should not happen, missing symbol table for function identifier {node.identifier.name}."

    @visit.register
    def _(self, node: ast.ExprStmtNode):
        self.do_visit(node.expr)

    @visit.register
    def _(self, node: ast.PassStmtNode):
        pass

    @visit.register
    def _(self, node: ast.IfStmtNode):
        self.do_visit(node.condition)
        if node.condition.get_type_str() != 'bool':
            self.type_error(node, node.condition.get_type_str(), 'bool')
        for s in node.then_body:
            self.do_visit(s)
        for e in node.elifs:
            self.do_visit(e[0])
            if e[0].get_type_str() != 'bool':
                self.type_error(node, e[0].get_type_str(), 'bool')
            for s in e[1]:
                self.do_visit(s)
        for s in node.else_body:
            self.do_visit(s)

    @visit.register
    def _(self, node: ast.TypeAnnotationNode):
        if not self.t_env.is_valid_typename(node.name):
            self.type_error(node, node.name, '<valid type>')

    @visit.register
    def _(self, node: ast.TypedVarNode):
        self.do_visit(node.identifier)
        self.do_visit(node.id_type)

    @visit.register
    def _(self, node: ast.VarDefNode):
        self.do_visit(node.var)
        self.do_visit(node.value)
        if not self.t_env.is_assign_comp(node.value.get_type_str(), node.var.id_type.to_str()):
            self.type_error(node, node.value.get_type_str(), node.var.id_type.to_str())

    @visit.register
    def _(self, node: ast.FuncDefNode):
        self.do_visit(node.name)
        self.t_env.enter_scope(node.name.name)
        for p in node.params:
            self.do_visit(p)
        self.do_visit(node.return_type)

        # Here we do the type checking of the function definition.
        module_st = self.t_env.get_symbol_table()
        scope_st = self.t_env.get_scope_symbol_table()
        parent_st = scope_st.get_parent()
        is_method = parent_st and parent_st.get_type() == 'class'
        signature = self.get_signature(scope_st)
        if is_method:
            if len(signature.args_type) == 0:  # A class method needs at least one argument ...
                self.type_error(node, '0 arguments', '1+ arguments')
            elif signature.args_type[0] != parent_st.get_name():  # ... of the same type as the enclosing class.
                self.type_error(node, signature.args_type[0], parent_st.get_name())
            else:  # We also need to ensure that the signatures of overriding methods are compatible.
                supertypes = self.t_env.get_supertypes_of(parent_st.get_name())
                for st in module_st.get_children():
                    if st.get_type() == 'class' and st.get_name() in supertypes:
                        if m_st := st.get_methods_sym_table(scope_st.get_name()):
                            super_signature = self.get_signature(m_st)
                            if not signature.method_compatible(super_signature, self.t_env):
                                self.type_error(node, str(signature), str(super_signature))

        for d in node.declarations:
            self.do_visit(d)
        for s in node.statements:
            self.do_visit(s)
        self.t_env.exit_scope()

    @visit.register
    def _(self, node: ast.ProgramNode):
        for d in node.declarations:
            self.do_visit(d)
        for s in node.statements:
            self.do_visit(s)

    #######################################################################
    # Finish writing the methods below.
    #######################################################################

    @visit.register
    def _(self, node: ast.UnaryOpExprNode):
        self.do_visit(node.operand)
        if node.op == Operator.Minus and node.operand.get_type_str() != 'int':
            self.type_error(node, node.operand.get_type_str(), 'int')
        elif node.op == Operator.Not and node.operand.get_type_str() != 'bool':
            self.type_error(node, node.operand.get_type_str(), 'bool')
        node.set_type_str(node.operand.get_type_str())

    @visit.register
    def _(self, node: ast.IfExprNode):
        self.do_visit(node.condition)
        if node.condition.get_type_str() != 'bool':
            self.type_error(node, node.condition.get_type_str(), 'bool')
        self.do_visit(node.then_expr)
        self.do_visit(node.else_expr)
        type_str = self.t_env.join(node.then_expr.get_type_str(), node.else_expr.get_type_str())
        node.set_type_str(type_str)

    @visit.register
    def _(self, node: ast.ReturnStmtNode):
        self.do_visit(node.expr)
        scope_st = self.t_env.get_scope_symbol_table()
        if scope_st.get_type() != 'function':
            # Opps, used a return statement outside a function (a syntax error, strictly speaking).
            self.invalid_use_error(node, "return statement used outside of a function")
        symbol = scope_st.get_parent().lookup(scope_st.get_name())
        assert symbol, f"Should not happen, identifier {scope_st.get_name()} not in scope or missing in symbol table."
        type_str_expr = node.expr.get_type_str() if node.expr else '<None>'
        if not self.t_env.is_assign_comp(type_str_expr, symbol.get_type_str()):
            self.type_error(node, type_str_expr, symbol.get_type_str())

    @visit.register
    def _(self, node: ast.AssignStmtNode):
        targets_type = []
        for t in node.targets:
            self.do_visit(t)
            if isinstance(t, ast.IdentifierExprNode):
                symbol = self.t_env.get_scope_symbol_table().lookup(t.identifier.name)
                if symbol.is_read_only():
                    self.invalid_use_error(node, f'Variable {t.identifier.name} is read-only.')
            targets_type.append(t.get_type_str())
        self.do_visit(node.expr)
        type_str_expr = node.expr.get_type_str()
        if len(targets_type) > 1 and type_str_expr == '[<None>]':
            self.type_error(node, node.expr.get_type_str(), 'multi-var-assignment')
        for type_str in targets_type:
            if not self.t_env.is_assign_comp(type_str_expr, type_str):
                self.type_error(node, type_str, type_str_expr)

    @visit.register
    def _(self, node: ast.WhileStmtNode):
        self.do_visit(node.condition)
        if node.condition.get_type_str() != 'bool':
            self.type_error(node, node.condition.get_type_str(), 'bool')
        for s in node.body:
            self.do_visit(s)
