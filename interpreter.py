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
        self.active_blocks = []
        self.debug = True  # Set to False after verification

    def start(self, tokens):
        for token in tokens:
            if self.debug:
                print(f"Processing start token: {token}")
            self.transform(token)
            if self.return_value is not None:
                if self.debug:
                    print(f"Stopping start due to return_value: {self.return_value}")
                break
        return self.return_value

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
        condition, block = args
        condition_value = self.transform(condition)
        if self.debug:
            print(
                f"Evaluating if condition: {condition_value}, active_blocks: {self.active_blocks}"
            )
        if condition_value:
            self.active_blocks.append(True)
            try:
                self.transform(block)
            finally:
                self.active_blocks.pop()
        else:
            self.active_blocks.append(False)
            if self.debug:
                print(
                    f"Skipping block due to false condition, active_blocks: {self.active_blocks}"
                )
            self.active_blocks.pop()
        return None

    def block(self, args):
        if not all(self.active_blocks):
            if self.debug:
                print(f"Skipping block, active_blocks: {self.active_blocks}")
            return None

        if self.debug:
            print(f"Executing block, active_blocks: {self.active_blocks}")
        for stmt in args:
            if self.debug:
                print(f"Processing statement: {stmt}")
            self.transform(stmt)
            if self.return_value is not None:
                if self.debug:
                    print(
                        f"Stopping block execution due to return_value: {self.return_value}"
                    )
                break
        return None

    def return_stmt(self, args):
        value = args[0] if args else "air"
        if all(self.active_blocks) or not self.active_blocks:
            if self.return_value is None:
                self.return_value = value
                if self.debug:
                    print(
                        f"Setting return_value to {self.return_value}, active_blocks: {self.active_blocks}"
                    )
            else:
                if self.debug:
                    print(
                        f"Ignoring return of {value} as return_value already set to {self.return_value}"
                    )
        else:
            if self.debug:
                print(
                    f"Skipping return of {value}, inactive block, active_blocks: {self.active_blocks}"
                )
        return None

    def assign_stmt(self, args):
        var_name, value = args
        if var_name not in ["x", "y", "z", "time"]:
            self.vars[var_name] = value
            if self.debug:
                print(f"Assigned {var_name} = {value}")
        return None

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
    return interpreter.return_value if interpreter.return_value is not None else "air"


def test_chained_ifs():
    def run_test(x, y, expected):
        print(f"\n\n\nRunning test with x={x}, y={y}, expected={expected}...")
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
    print("Parse tree:")
    print(parser.parse(code).pretty())

    success_count = 0
    print("\nTesting nested conditionals:\n\n\n")
    run_test(8, 2, "grass")  # Both conditions true
    run_test(8, 4, "stone")  # Outer true, inner false
    run_test(4, 1, "air")  # Outer false
    run_test(6, 2.9, "grass")  # Boundary case
    run_test(5.1, 3, "stone")  # Boundary case

    print(f"\n\n\nPassed {success_count}/5 tests")


if __name__ == "__main__":
    test_chained_ifs()
    print("All tests completed.")
