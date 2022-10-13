from parser_sol import Parser
from print_visitor import PrintVisitor

filename = "test_parser.py"
with open(filename) as f:
    p = Parser(f)
    a = p.parse()
    pv = PrintVisitor()
    pv.do_visit(a)
