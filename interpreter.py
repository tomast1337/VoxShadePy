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
        self.result_stack = []
        self.skip_level = None

    def log(self, *args):
        if self.debug:
            print("DEBUG:", *args)

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
        if self.skip_level is not None:
            return

        condition, block = args
        if not condition:
            # Skip this entire block
            self.skip_level = len(self.result_stack)
            self.transform(block)
            self.skip_level = None
        else:
            self.transform(block)

    def block(self, args):
        if self.skip_level is not None and len(self.result_stack) >= self.skip_level:
            return
            
        for stmt in args:
            self.transform(stmt)
            if len(self.result_stack) > 0:  # Found a return
                break

    def return_stmt(self, args):
        if self.skip_level is not None and len(self.result_stack) >= self.skip_level:
            return

        self.result_stack.append(args[0] if args else "air")

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
    interpreter = ShaderInterpreter()
    interpreter.vars.update({"x": x, "y": y, "z": z, "time": time})
    parser = Lark(GRAMMAR, parser="lalr")
    tree = parser.parse(code)
    interpreter.transform(tree)
    return interpreter.result_stack[-1] if interpreter.result_stack else "air"


def test_chained_ifs():
    def run_test(x, y, expected):
        nonlocal success_count
        result = run_shader(code, x=x, y=y, z=0, time=0)
        print(f"Test (x={x}, y={y}): {result} ", end="")
        if result == expected:
            print("✓")
            success_count += 1
        else:
            print(f"✗ (expected {expected})")

    code = """
    if (x > 5.0) {
        if (y < 3.0) {
            return grass;
        }
        return stone;
    }
    return air;
    """

    parser = Lark(GRAMMAR, parser="lalr")
    code = """
    if (x > 5.0) {
        if (y < 3.0) {
            return grass;
        }
        return stone;
    }
    return air;
    """
    print("Parse tree:")
    print(parser.parse(code).pretty())

    success_count = 0
    print("\nTesting nested conditionals:")
    run_test(8, 2, "grass")  # Both conditions true
    run_test(8, 4, "stone")  # Outer true, inner false
    run_test(4, 1, "air")  # Outer false
    run_test(6, 2.9, "grass")  # Boundary case
    run_test(5.1, 3, "stone")  # Boundary case

    print(f"\nPassed {success_count}/5 tests")


if __name__ == "__main__":
    test_chained_ifs()
