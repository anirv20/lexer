#
#  Java Byte Code Instructions. Version 1.00
#
from typing import Optional
from enum import Enum, auto


class BC:

    class InstrCode(Enum):
        # Load and store instructions.
        aload = auto()
        astore = auto()
        fload = auto()
        fstore = auto()
        iload = auto()
        istore = auto()
        aaload = auto()
        aastore = auto()
        baload = auto()
        bastore = auto()
        iaload = auto()
        iastore = auto()
        faload = auto()
        fastore = auto()
        getstatic = auto()
        putstatic = auto()
        getfield = auto()
        putfield = auto()
        # Operations
        iadd = auto()
        idiv = auto()
        imul = auto()
        isub = auto()
        ineg = auto()
        irem = auto(),
        fadd = auto()
        fdiv = auto()
        fmul = auto()
        fsub = auto()
        fneg = auto()
        # Jumping instructions
        ifeq = auto()
        ifne = auto()
        ifgt = auto()
        ifge = auto()
        iflt = auto()
        ifle = auto()
        if_icmpeq = auto()
        if_icmpne = auto()
        if_icmpgt = auto()
        if_icmpge = auto()
        if_icmplt = auto()
        if_icmple = auto()
        goto = auto()
        # Methods calls and return statements.
        invokestatic = auto()
        invokespecial = auto()
        invokevirtual = auto()
        return_ = auto()
        areturn = auto()
        ireturn = auto()
        freturn = auto()
        # Various
        fcmpl = auto()
        new = auto(),
        newarray = auto()
        anewarray = auto()
        i2f = auto()
        ldc = auto()
        pop = auto()
        dup = auto()
        swap = auto()
        nop = auto()
        aconst_null = auto()

    @staticmethod
    def instr_code_to_name(instr_code: InstrCode) -> str:
        instr_code_names = {
            BC.InstrCode.aload: "aload",
            BC.InstrCode.astore: "astore",
            BC.InstrCode.fload: "fload",
            BC.InstrCode.fstore: "fstore",
            BC.InstrCode.iload: "iload",
            BC.InstrCode.istore: "istore",
            BC.InstrCode.aaload: "aaload",
            BC.InstrCode.aastore: "aastore",
            BC.InstrCode.baload: "baload",
            BC.InstrCode.bastore: "bastore",
            BC.InstrCode.faload: "faload",
            BC.InstrCode.fastore: "fastore",
            BC.InstrCode.iaload: "iaload",
            BC.InstrCode.iastore: "iastore",
            BC.InstrCode.getstatic: "getstatic",
            BC.InstrCode.putstatic: "putstatic",
            BC.InstrCode.getfield: "getfield",
            BC.InstrCode.putfield: "putfield",
            BC.InstrCode.invokespecial: "invokespecial",
            BC.InstrCode.invokestatic: "invokestatic",
            BC.InstrCode.invokevirtual: "invokevirtual",
            BC.InstrCode.return_: "return",
            BC.InstrCode.areturn: "areturn",
            BC.InstrCode.ireturn: "ireturn",
            BC.InstrCode.freturn: "freturn",
            BC.InstrCode.ldc: "ldc",
            BC.InstrCode.ifeq: "ifeq",
            BC.InstrCode.ifne: "ifne",
            BC.InstrCode.ifgt: "ifgt",
            BC.InstrCode.ifge: "ifge",
            BC.InstrCode.iflt: "iflt",
            BC.InstrCode.ifle: "ifle",
            BC.InstrCode.if_icmpeq: "if_icmpeq",
            BC.InstrCode.if_icmpne: "if_icmpne",
            BC.InstrCode.if_icmpgt: "if_icmpgt",
            BC.InstrCode.if_icmpge: "if_icmpge",
            BC.InstrCode.if_icmplt: "if_icmplt",
            BC.InstrCode.if_icmple: "if_icmple",
            BC.InstrCode.goto: "goto",
            BC.InstrCode.fcmpl: "fcmpl",
            BC.InstrCode.new: "new",
            BC.InstrCode.newarray: "newarray",
            BC.InstrCode.anewarray: "anewarray",
            BC.InstrCode.i2f: "i2f",
            BC.InstrCode.pop: "pop",
            BC.InstrCode.dup: "dup",
            BC.InstrCode.swap: "swap",
            BC.InstrCode.nop: "nop",
            BC.InstrCode.iadd: "iadd",
            BC.InstrCode.isub: "isub",
            BC.InstrCode.idiv: "idiv",
            BC.InstrCode.imul: "imul",
            BC.InstrCode.ineg: "ineg",
            BC.InstrCode.irem: "irem",
            BC.InstrCode.fadd: "fadd",
            BC.InstrCode.fsub: "fsub",
            BC.InstrCode.fdiv: "fdiv",
            BC.InstrCode.fmul: "fmul",
            BC.InstrCode.fneg: "fneg",
            BC.InstrCode.aconst_null: "aconst_null"
        }
        return instr_code_names[instr_code]

    class Label:

        num: int = 0

        def __init__(self):
            self._num = BC.Label.num
            BC.Label.num += 1

        def __str__(self) -> str:
            return "L_" + str(self._num)

        def get_num(self) -> int:
            return self._num

    class Instr:

        def __init__(self, instr_code: "BC.InstrCode", args: Optional[list[str]] = None):
            self._instr_code: BC.InstrCode = instr_code
            self._args: list[str] = [] if args is None else args
            self._label: Optional[BC.Label] = None

        def __str__(self):
            return self.to_string()

        def get_instr_code(self):
            return self._instr_code

        def get_label(self):
            return self._label

        def get_args(self):
            return self._args

        def set_label(self, label: "BC.Label"):
            self._label = label

        def to_string(self) -> str:
            s = ''
            if self._label and self._label.get_num() >= 0:
                s += str(self._label) + ':\t'
            s += BC.instr_code_to_name(self._instr_code)
            for a in self._args:
                s += ' ' + a
            return s
