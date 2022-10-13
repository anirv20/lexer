#
# Test semantic analyser. Version 1.2
from parser_david import Parser
import disp_symtable
import semantic_error
import symtab_visitor as symtable_visitor
import type_env
import type_visitor
import print_visitor


filename = 'test/test03.cpy'

# Read in and print out the code.
with open(filename) as f:
    code = f.read()
print(code)

# Parse the code.
with open(filename) as f:
    p = Parser(f)
    ast = p.parse()
    #pv = print_visitor.PrintVisitor()
    #pv.do_visit(ast)

# Do the symbol-table construction.
try:
    st_visitor = symtable_visitor.SymbolTableVisitor()
    st_visitor.do_visit(ast)
except semantic_error.CompilerException as e:
    print(e.message)
    exit(-1)
st = st_visitor.get_symbol_table()
ds = disp_symtable.DispSymbolTable()
ds.print_symtable(st)

# Do the type checking.
te = type_env.TypeEnvironment(st)
try:
    t_visitor = type_visitor.TypeVisitor(te)
    t_visitor.do_visit(ast)
except semantic_error.CompilerException as e:
    print(e.message)
    exit(-1)

p_visitor = print_visitor.PrintVisitor()
p_visitor.do_visit(ast)
