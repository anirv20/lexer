#
# ASTree version 1.07
#

from enum import Enum
from typing import Optional


class Operator(Enum):
    Or = 0
    And = 1
    Not = 2
    Eq = 3
    NotEq = 4
    Lt = 5
    Gt = 6
    LtEq = 7
    GtEq = 8
    Is = 9
    Plus = 10
    Minus = 11
    Mult = 12
    IntDivide = 13
    Modulus = 14


class Node:

    def __str__(self):
        return self.__class__.__name__ \
               + (' ' + str(self.name) if hasattr(self, "name") else '') \
               + (' ' + str(self.identifier) if hasattr(self, "identifier") else '')


class IdentifierNode(Node):

    def __init__(self, name: str):
        self.name = name


#######################################################


class ExprNode(Node):

    def __init__(self):
        self.type_str = ""

    def get_type_str(self):
        return self.type_str

    def set_type_str(self, type_str: str):
        self.type_str = type_str


class LiteralExprNode(ExprNode):

    def __init__(self):
        super().__init__()


class IntegerLiteralExprNode(LiteralExprNode):

    def __init__(self, value: int):
        super().__init__()
        self.value = value


class BooleanLiteralExprNode(LiteralExprNode):

    def __init__(self, value: bool):
        super().__init__()
        self.value = value


class IdentifierExprNode(ExprNode):

    def __init__(self, identifier: IdentifierNode):
        super().__init__()
        self.identifier = identifier


class BinaryOpExprNode(ExprNode):

    def __init__(self, op: Operator, lhs: ExprNode, rhs: ExprNode):
        super().__init__()
        self.op = op
        self.lhs = lhs
        self.rhs = rhs


class UnaryOpExprNode(ExprNode):

    def __init__(self, op: Operator, operand: ExprNode):
        super().__init__()
        self.op = op
        self.operand = operand


class IfExprNode(ExprNode):

    def __init__(self, condition: ExprNode, then_expr: ExprNode, else_expr: ExprNode):
        super().__init__()
        self.condition = condition
        self.then_expr = then_expr
        self.else_expr = else_expr


class FunctionCallExprNode(ExprNode):

    def __init__(self, identifier: IdentifierNode, args: list[ExprNode]):
        super().__init__()
        self.identifier = identifier
        self.args = args


#######################################################


class StmtNode(Node):
    pass


class ExprStmtNode(StmtNode):

    def __init__(self, expr: ExprNode):
        self.expr = expr


class PassStmtNode(StmtNode):

    def __init__(self):
        pass


class ReturnStmtNode(StmtNode):

    def __init__(self, expr: Optional[ExprNode]):
        self.expr = expr


class AssignStmtNode(StmtNode):

    def __init__(self, targets: list[ExprNode], expr: ExprNode):
        self.targets = targets
        self.expr = expr


class IfStmtNode(StmtNode):

    def __init__(self, condition: ExprNode, then_body: list[StmtNode],
                 elifs: list[Optional[tuple[ExprNode, list[StmtNode]]]], else_body: list[StmtNode]):
        self.condition = condition
        self.then_body = then_body
        self.elifs = elifs
        self.else_body = else_body


class WhileStmtNode(StmtNode):

    def __init__(self, condition: ExprNode, body: list[StmtNode]):
        self.condition = condition
        self.body = body


#######################################################


class TypeAnnotationNode(Node):

    def __init__(self, name: str):
        self.name = name

    def to_str(self):
        return self.name


class TypedVarNode(Node):

    def __init__(self, identifier: IdentifierNode, id_type: TypeAnnotationNode):
        self.identifier = identifier
        self.id_type = id_type


class DeclarationNode(Node):
    pass


class VarDefNode(DeclarationNode):

    def __init__(self, var: TypedVarNode, value: LiteralExprNode):
        self.var = var
        self.value = value


class FuncDefNode(DeclarationNode):

    def __init__(self, name: IdentifierNode, params: list[Optional[TypedVarNode]],
                 return_type: Optional[TypeAnnotationNode], declarations: list[Optional[DeclarationNode]],
                 statements: list[StmtNode]):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.declarations = declarations
        self.statements = statements


class ProgramNode(Node):

    def __init__(self, declarations: list[Optional[DeclarationNode]], statements: list[Optional[StmtNode]]):
        self.declarations = declarations
        self.statements = statements
