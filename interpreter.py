from lark import Lark, Transformer, v_args
import numpy as np

with open("voxel_grammar.lark") as f:
    GRAMMAR = f.read()


# Interpreter implementation
class ShaderInterpreter(Transformer):
    def __init__(self):
        self.vars = {}
        self.return_value = None
        self.should_return = False

    # Built-in functions
    def sin(self, args):
        return math.sin(args[0])

    def cos(self, args):
        return math.cos(args[0])

    def noise(self, args):
        # Simple deterministic pseudo-noise
        x, y, *rest = args
        x *= 12.9898
        y *= 78.233
        return math.fmod(math.sin(x + y) * 43758.5453, 1.0)

    # Operations
    def add(self, args):
        return args[0] + args[1]

    def sub(self, args):
        return args[0] - args[1]

    def mul(self, args):
        return args[0] * args[1]

    def div(self, args):
        return args[0] / args[1]

    def compare(self, args):
        if len(args) == 1:  # Just a single value
            return args[0]

        op = args[1]
        a, b = args[0], args[2]

        # Handle number comparisons properly
        if isinstance(a, str) and a.replace(".", "", 1).isdigit():
            a = float(a)
        if isinstance(b, str) and b.replace(".", "", 1).isdigit():
            b = float(b)

        if op == "==":
            return a == b
        if op == "!=":
            return a != b
        if op == "<":
            return a < b
        if op == ">":
            return a > b
        if op == "<=":
            return a <= b
        if op == ">=":
            return a >= b
        return False

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
    import math  # Add this at the top of the function

    parser = Lark(GRAMMAR, parser="lalr")
    interpreter = ShaderInterpreter()
    interpreter.vars.update(
        {"x": float(x), "y": float(y), "z": float(z), "time": float(time)}
    )
    tree = parser.parse(code)
    interpreter.transform(tree)
    return interpreter.return_value or "air"
