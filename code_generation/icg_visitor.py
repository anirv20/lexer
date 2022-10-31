#
# ICGVisitor version 1.00
#
import functools
import pathlib
import astree as ast
from astree import Operator
import visitor
from bc import BC


STACK_SIZE = 20  # A dirty hack, instead of computing correct stack size, give a large one and hope for the best!

# Binary arithmetic operators and their bytecode instructor identifier.
arithm_ops = {Operator.Plus: BC.InstrCode.iadd,
              Operator.Minus: BC.InstrCode.isub,
              Operator.Mult: BC.InstrCode.imul,
              Operator.IntDivide: BC.InstrCode.idiv,
              Operator.Modulus: BC.InstrCode.irem}

# Relational comparison operators and their bytecode instructor identifier.
rel_ops = {Operator.Eq: BC.InstrCode.if_icmpeq,
           Operator.NotEq: BC.InstrCode.if_icmpne,
           Operator.Lt: BC.InstrCode.if_icmplt,
           Operator.LtEq: BC.InstrCode.if_icmple,
           Operator.Gt: BC.InstrCode.if_icmpgt,
           Operator.GtEq: BC.InstrCode.if_icmpge}


class ICGVisitor(visitor.Visitor):

    # A wrapper allowing us to use 'load' with a variable's name rather than its local number.
    def bc_load(self, name: str) -> BC.Instr:
        return BC.Instr(BC.InstrCode.iload, [str(self._locals[-1].index(name))])

    # A wrapper allowing us to use 'store' with a variable's name rather than its local number.
    def bc_store(self, name: str) -> BC.Instr:
        return BC.Instr(BC.InstrCode.istore, [str(self._locals[-1].index(name))])

    # Append an instruction to the program.
    def emit(self, instr: BC.Instr):
        self._program.append(str(instr))

    # Append a label to the program.
    def emit_label(self, label: BC.Label):
        self._program.append(str(label) + ':')

    # Reformat the code to look a bit more print friendly.
    @staticmethod
    def reformat(program: list[str]) -> list[str]:
        program_out = []
        indent = 0
        for instr in program:
            text = str(instr)
            if text.startswith('.end method') or text.startswith('.end code'):
                indent -= 1
            elif text.startswith('.method') or text.startswith('.end class'):
                program_out.append('')
            if text.startswith('L_'):
                text = ' ' * (4*indent-2) + text
            else:
                text = ' ' * (4*indent) + text
            program_out.append(text)
            if text.startswith('.method') or text.startswith(".code"):
                indent += 1
        return program_out

    # Write the assembly (JBC) out to a file.
    @staticmethod
    def write_asm_file(output_dir: str, program_name: str, program: list[str]):
        p = pathlib.Path(output_dir, program_name + '.j')
        with open(str(p), 'w') as f:
            for instr in program:
                f.write(str(instr))
                f.write('\n')

    @staticmethod
    def jvm_signature(no_params: int) -> str:
        return '(' + 'I' * no_params + ')I'

    ######################################################################

    def __init__(self, program_name: str):
        self._program_name: str = program_name
        self._locals = []
        self._program = []
        self.init()

    def get_program(self) -> list[str]:
        return self._program

    def init(self):
        self._locals: list[list[str]] = []
        self._program: list[str] = [
            '.version 49 0',
            f'.class public super {self._program_name}',
            '.super java/lang/Object',
            '.method public <init> : ()V',
            '.code stack 1 locals 1',
            'aload_0',
            'invokespecial Method java/lang/Object <init> ()V',
            'return',
            '.end code',
            '.end method',
            '.method static print : (I)I',
            '.code stack 2 locals 1',
            'getstatic Field java/lang/System out Ljava/io/PrintStream;',
            'iload_0',
            'invokevirtual Method java/io/PrintStream println (I)V',
            'iconst_0',
            'ireturn',
            '.end code',
            '.end method']

    def do_visit(self, node):
        if node:
            self.visit(node)

    @functools.singledispatchmethod
    def visit(self, node):
        print("Visitor support missing for", type(node))
        exit()

    @visit.register
    def _(self, node: ast.IdentifierNode):
        ...  # Do nothing.

    @visit.register
    def _(self, node: ast.IntegerLiteralExprNode):
        self.emit(BC.Instr(BC.InstrCode.ldc, [str(node.value)]))

    @visit.register
    def _(self, node: ast.UnaryOpExprNode):
        self.do_visit(node.operand)
        if node.op == Operator.Minus:
            self.emit(BC.Instr(BC.InstrCode.ineg))
        elif node.op == Operator.Not:
            label_true = BC.Label()
            label_end = BC.Label()
            self.emit(BC.Instr(BC.InstrCode.ifeq, [str(label_true)]))
            self.emit(BC.Instr(BC.InstrCode.ldc, ['0']))
            self.emit(BC.Instr(BC.InstrCode.goto, [str(label_end)]))
            self.emit_label(label_true)
            self.emit(BC.Instr(BC.InstrCode.ldc, ['1']))
            self.emit_label(label_end)
        else:
            assert False, "ERROR: Internal compiler error, should not happen."

    @visit.register
    def _(self, node: ast.FunctionCallExprNode):
        self.do_visit(node.identifier)
        for a in node.args:
            self.do_visit(a)
        self._program.append(BC.Instr(BC.InstrCode.invokestatic,
                                      ['Method', self._program_name, node.identifier.name,
                                       self.jvm_signature(len(node.args))]))

    @visit.register
    def _(self, node: ast.ExprStmtNode):
        self.do_visit(node.expr)
        # If the result of expression is not consumed (as in expression statements), we must manually discard it.
        self.emit(BC.Instr(BC.InstrCode.pop))

    @visit.register
    def _(self, node: ast.PassStmtNode):
        self.emit(BC.Instr(BC.InstrCode.nop))

    @visit.register
    def _(self, node: ast.ReturnStmtNode):
        self.do_visit(node.expr)
        if not node.expr:
            self.emit(BC.Instr(BC.InstrCode.ldc, ['0']))  # Returns 0 by default, if no expression.
        self.emit(BC.Instr(BC.InstrCode.ireturn))

    @visit.register
    def _(self, node: ast.TypeAnnotationNode):
        pass  # Do nothing ...

    @visit.register
    def _(self, node: ast.TypedVarNode):
        # self.do_visit(node.identifier)
        # self.do_visit(node.id_type)
        self._locals[-1].append(node.identifier.name)

    @visit.register
    def _(self, node: ast.VarDefNode):
        self.do_visit(node.var)
        self.do_visit(node.value)
        self.emit(self.bc_store(node.var.identifier.name))

    @visit.register
    def _(self, node: ast.FuncDefNode):
        self._locals.append([])
        signature = self.jvm_signature(len(node.params))
        self._program.append(f'.method static {node.name.name} : {signature}')
        pos = len(self._program)
        # self.do_visit(node.name)
        for p in node.params:
            self.do_visit(p)
        self.do_visit(node.return_type)
        for d in node.declarations:
            self.do_visit(d)
        # Now that we know the number of local variables, we can add the '.code' macro.
        self._program.insert(pos, f'.code stack {STACK_SIZE} locals {len(self._locals)}  ; {str(self._locals[-1])}')
        for s in node.statements:
            self.do_visit(s)
        if not self._program[-1].startswith('ireturn'):
            # Ensure that a function returns (with a default value 0) in case there are fall-through execution paths.
            self.emit(BC.Instr(BC.InstrCode.ldc, ['0']))
            self.emit(BC.Instr(BC.InstrCode.ireturn))
        self._program.append('.end code')
        self._program.append('.end method')
        self._locals.pop()

    @visit.register
    def _(self, node: ast.ProgramNode):
        self.init()
        self._locals.append([])
        self._locals[-1].append('<args>')  # JVM, the main method always takes one argument (albeit, not used by us).
        for d in node.declarations:
            self.do_visit(d)
        self._program.append('.method public static main : ([Ljava/lang/String;)V')
        self._program.append(f'.code stack {STACK_SIZE} locals {len(self._locals)}  ; {str(self._locals[-1])}')
        for s in node.statements:
            self.do_visit(s)
        self.emit(BC.Instr(BC.InstrCode.return_))
        self._program.append('.end code')
        self._program.append('.end method')
        self._program.append('.end class')
        self._locals.pop()

    #######################################################################################################
    # Your task is to finish implementing the below methods ...
    # You might find it helpful to first study the code above, as an example of how to generate bytecode
    # by calling the self.emit, self.emit_label functions.
    # You, will also find the convenience functions self.bc_load and self.bc_store helpful.
    #######################################################################################################

    @visit.register
    def _(self, node: ast.BooleanLiteralExprNode):
        # Hints:
        #  - Boolean values are represented with integers (0: False, 1: True)
        if node.value:
            self.emit(BC.Instr(BC.InstrCode.ldc, ['1']))
        else:
            self.emit(BC.Instr(BC.InstrCode.ldc, ['0']))

    @visit.register
    def _(self, node: ast.IdentifierExprNode):
        self.do_visit(node.identifier)
        self.bc_load(node.identifier.name)

    @visit.register
    def _(self, node: ast.BinaryOpExprNode):
        # Hints:
        #  - You might find the arithm_ops and rel_ops dictionaries defined above helpful.
        #  - Also, remember the logical binary operators ('and' and 'or') and remember their short-circuiting.
        
        #leaves lhs and rhs on the stack
        
        l_end = BC.Label()
        if node.op in rel_ops:
            l_true = BC.Label()
            self.do_visit(node.lhs)
            self.do_visit(node.rhs)
            self.emit(BC.Instr(rel_ops[node.op], [str(l_true)]))
            self.emit(BC.Instr(BC.InstrCode.ldc, ["0"]))
            self.emit(BC.Instr(BC.InstrCode.goto, [str(l_end)]))
            self.emit_label(l_true)
            self.emit(BC.Instr(BC.InstrCode.ldc, ["1"]))
        elif node.op == Operator.And:
            l_false = BC.Label()
            self.do_visit(node.lhs)
            self.emit(BC.Instr(BC.InstrCode.ifeq, [str(l_false)]))
            self.do_visit(node.rhs)
            self.emit(BC.Instr(BC.InstrCode.ifeq, [str(l_false)]))
            self.emit(BC.Instr(BC.InstrCode.ldc, ["1"]))
            self.emit(BC.Instr(BC.InstrCode.goto, [str(l_end)]))
            self.emit_label(l_false)
            self.emit(BC.Instr(BC.InstrCode.ldc, ["0"]))
        elif node.op == Operator.Or:
            l_false = BC.Label()
            self.do_visit(node.lhs)
            self.do_visit(node.rhs)
            self.emit(BC.Instr(BC.InstrCode.iadd))
            self.emit(BC.Instr(BC.InstrCode.ifeq, [str(l_false)]))
            self.emit(BC.Instr(BC.InstrCode.ldc, ["1"]))
            self.emit(BC.Instr(BC.InstrCode.goto, [str(l_end)]))
            self.emit_label(l_false)
            self.emit(BC.Instr(BC.InstrCode.ldc, ["0"]))
        self.emit_label(l_end)

        # iload lhs
        # iload rhs
        # if_icmpxx goto l1
        # ldc 0
        # goto end
        # l1:
        # ldc 1
        # end

    @visit.register
    def _(self, node: ast.IfExprNode):
        self.do_visit(node.condition)
        self.do_visit(node.then_expr)
        self.do_visit(node.else_expr)

    @visit.register
    def _(self, node: ast.WhileStmtNode):
        self.do_visit(node.condition)
        for s in node.body:
            self.do_visit(s)

    @visit.register
    def _(self, node: ast.IfStmtNode):
        # Hints:
        #  - Do not worry if you end up creating some unnecessary labels (doing so might simplify your
        #    implementation a bit, e.g., by jumping to the 'else' part without checking if it exists).
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
    def _(self, node: ast.AssignStmtNode):
        # Hints:
        #  - Do not visit the targets (not to generate 'load'), instead access them from here, e.g. 't.identifier.name'
        #  - The target is always going to be of type 'ast.IdentifierExprNode' in our simplified version.
        #  - If there are more than one targets you will need to duplicate the expression value on the stack
        #    for all but the last target.

        self.do_visit(node.expr)
        for t in node.targets:
            # self.do_visit(t)
            if isinstance(t, ast.IdentifierExprNode):
                ...
            else:
                assert False, "ERROR: Internal compiler error, should not happen."
