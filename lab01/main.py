import parser_lab as parser
filename = 'test_bool_expr.txt'
with open(filename) as f:
    parser = parser.Parser(f)
    parser.parse()

