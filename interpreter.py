from lark import Lark, Transformer
import numpy as np

with open("voxel_grammar.lark") as f:
    GRAMMAR = f.read()


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


MATERIALS = {
    "air",
    "stone",
    "water",
    "grass",
    "crystal",
    "sand",
    "wood",
    "metal",
    "lava",
    "ice",
    "dirt",
    "snow",
    "cloud",
    "glass",
    "brick",
    "obsidian",
}


class ShaderInterpreter(Transformer):

    def __init__(self):
        self.vars = {"x": 0.0, "y": 0.0, "z": 0.0, "time": 0.0}
        self.return_value = None
        self.return_encountered = False  # New flag to track returns

    # Constant variables
    def x_var(self, args):
        return self.vars["x"]

    def y_var(self, args):
        return self.vars["y"]

    def z_var(self, args):
        return self.vars["z"]

    def time_var(self, args):
        return self.vars["time"]

    # Variable and material handling
    def var(self, args):
        if not args:
            return 0.0
        name = str(args[0])
        return self.vars.get(name, 0.0)

    def material(self, args):
        return str(args[0])

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
        left = args[0]
        for i in range(1, len(args), 2):
            op, right = args[i], args[i + 1]
            if op == "==":
                result = left == right
            elif op == "!=":
                result = left != right
            elif op == "<":
                result = left < right
            elif op == ">":
                result = left > right
            elif op == "<=":
                result = left <= right
            elif op == ">=":
                result = left >= right
            else:
                result = False
            left = result
        return left

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

    # Control flow
    def if_stmt(self, args):
        if len(args) != 2 or self.return_encountered:
            return
        condition, block = args
        if condition:
            self.transform(block)

    def block(self, args):
        for stmt in args:
            if self.return_encountered:
                break
            self.transform(stmt)

    def return_stmt(self, args):
        if not self.return_encountered:  # Only process first return
            self.return_value = args[0] if args else "air"
            self.return_encountered = True
        return self.return_value  # Return normally but set flag

    def assign_stmt(self, args):
        var_name, value = args
        if var_name not in ["x", "y", "z", "time"]:
            self.vars[var_name] = value

    # Token handling
    def NUMBER(self, token):
        return float(token.value)

    def NAME(self, token):
        return str(token.value)

    # Operators
    def eq_op(self, args):
        return "=="

    def neq_op(self, args):
        return "!="

    def lt_op(self, args):
        return "<"

    def gt_op(self, args):
        return ">"

    def lte_op(self, args):
        return "<="

    def gte_op(self, args):
        return ">="


def run_shader(code, x=0, y=0, z=0, time=0):
    parser = Lark(GRAMMAR, parser="lalr")
    interpreter = ShaderInterpreter()
    interpreter.vars.update(
        {"x": float(x), "y": float(y), "z": float(z), "time": float(time)}
    )
    tree = parser.parse(code)
    interpreter.transform(tree)
    return interpreter.return_value if interpreter.return_encountered else "air"


def test_shader():
    code = """
    if (x == 8.0) {
        return grass;
    }
    return air;
    """
    result = run_shader(code, x=8, y=2, z=3, time=4)
    print(result)  # Should output "grass"


if __name__ == "__main__":
    test_shader()
