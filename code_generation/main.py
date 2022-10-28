#
# Java-Byte-Code (JBC) generation for a simplified version of ChocoPy.
#
# Simplifications:
# - Only int and bool types are supported (i.e., no strings, lists, or classes).
# - Inner functions are not allowed.
# - Global variable declarations are not allowed.
# - The only built-in function is print(int).
# - There is no 'is' operator.
# - There is no 'for' statement.
# - All functions are required to return an int (return 0 by default).
#
#  This program compiles a given simplified ChocoPy program to Java byte-code.
#  The bytecode can then be compiled to a class file using hte Krakatau assember (as we did in the lab).
#
import pathlib
import error
import parser
import type_env
import symtable_visitor
import disp_symtable
import type_visitor
import print_visitor
import icg_visitor


def compile_to_jbc(file: pathlib.Path, out_dir: str, do_display_st=False, do_display_ast=False):
    print(f"Compiling ChocoPy file '{file.name}'.")
    with open(str(file)) as f:
        p = parser.Parser(f)
        ast = p.parse()
        sv = symtable_visitor.SymbolTableVisitor()
        sv.do_visit(ast)
        if do_display_st:
            ds = disp_symtable.DispSymbolTable()
            ds.print_symtable(sv.get_symbol_table())
        te = type_env.TypeEnvironment(sv.get_symbol_table())
        tv = type_visitor.TypeVisitor(te)
        tv.do_visit(ast)
        if do_display_ast:
            pv = print_visitor.PrintVisitor()
            pv.do_visit(ast)
        iv = icg_visitor.ICGVisitor(file.stem)
        iv.do_visit(ast)
        iv.write_asm_file(out_dir, file.stem, iv.reformat(iv.get_program()))


dir_name_tests = 'tests'
output_dir = 'outputs'
test_dir = pathlib.Path(dir_name_tests)
for entry in test_dir.iterdir():
    print(entry)
    if entry.is_file() and entry.suffix == '.cpy':
        try:
            compile_to_jbc(entry, output_dir, False, False)  # Flags are used to additional turn printing on/off.
        except error.SyntaxErrorException as e:
            print(e.message, e.location)
        except error.CompilerException as e:
            print(e.message)
