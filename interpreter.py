from lark import Lark, Transformer
import numpy as np

with open("voxel_grammar.lark") as f:
    GRAMMAR = f.read()


class ShaderInterpreter(Transformer):
    def __init__(self):
        self.vars = {}
        self.return_value = None
        self.should_return = False

    # Built-in functions
    def sin(self, args):
        return np.sin(args[0])

    def cos(self, args):
        return np.cos(args[0])

    def noise(self, args):
        x, y, *rest = args
        x *= 12.9898
        y *= 78.233
        return np.fmod(np.sin(x + y) * 43758.5453, 1.0)

    # Expression handling
    def comp_expr(self, args):
        if len(args) == 1:
            return args[0]
        result = args[0]
        for i in range(1, len(args), 2):
            op, right = args[i], args[i + 1]
            if op == "==":
                result = result == right
            elif op == "!=":
                result = result != right
            elif op == "<":
                result = result < right
            elif op == ">":
                result = result > right
            elif op == "<=":
                result = result <= right
            elif op == ">=":
                result = result >= right
        return result

    def arith_expr(self, args):
        result = args[0]
        for i in range(1, len(args), 2):
            op, num = args[i], args[i + 1]
            if op == "+":
                result += num
            elif op == "-":
                result -= num
        return result

    def term_expr(self, args):
        result = args[0]
        for i in range(1, len(args), 2):
            op, num = args[i], args[i + 1]
            if op == "*":
                result *= num
            elif op == "/":
                result /= num
        return result

    # Statements
    def if_stmt(self, args):
        condition, block = args
        if condition:
            self.transform(block)

    def block(self, args):
        for stmt in args:
            if self.should_return:
                break
            self.transform(stmt)

    def return_stmt(self, args):
        self.return_value = args[0]
        self.should_return = True

    def assign_stmt(self, args):
        var_name, value = args
        self.vars[var_name] = value

    # Atoms
    def var(self, args):
        name = str(args[0])
        if name in ["x", "y", "z", "time"]:
            return self.vars.get(name, 0.0)
        return self.vars.get(name, 0.0)

    def material(self, args):
        return str(args[0])

    def NUMBER(self, token):
        return float(token.value)

    def NAME(self, token):
        return str(token.value)


def run_shader(code, x=0, y=0, z=0, time=0):
    parser = Lark(GRAMMAR, parser="lalr")
    interpreter = ShaderInterpreter()
    interpreter.vars.update(
        {"x": float(x), "y": float(y), "z": float(z), "time": float(time)}
    )
    tree = parser.parse(code)
    interpreter.transform(tree)
    return interpreter.return_value or "air"
