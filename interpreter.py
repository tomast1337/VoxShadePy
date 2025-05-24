from lark import Lark, Transformer
import numpy as np

with open("voxel_grammar.lark") as f:
    GRAMMAR = f.read()


class ShaderInterpreter(Transformer):
    def __init__(self):
        self.vars = {"x": 0.0, "y": 0.0, "z": 0.0, "time": 0.0}
        self.return_value = None
        self.should_return = False

    # Constant variables
    def x_var(self, args):
        return self.vars["x"]

    def y_var(self, args):
        return self.vars["y"]

    def z_var(self, args):
        return self.vars["z"]

    def time_var(self, args):
        return self.vars["time"]

    # Regular variable
    def var(self, args):
        if not args:
            return 0.0
        name = str(args[0])
        return self.vars.get(name, 0.0)

    # Material
    def material(self, args):
        if not args:
            return "air"
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
            op_tree = args[i]
            right = args[i + 1]

            # Extract the actual operator string
            op = op_tree.children[0] if hasattr(op_tree, "children") else str(op_tree)

            # Convert to numbers if needed
            left_num = (
                float(left)
                if isinstance(left, (int, float, str))
                and str(left).replace(".", "", 1).isdigit()
                else left
            )
            right_num = (
                float(right)
                if isinstance(right, (int, float, str))
                and str(right).replace(".", "", 1).isdigit()
                else right
            )

            if op == "==":
                result = left_num == right_num
            elif op == "!=":
                result = left_num != right_num
            elif op == "<":
                result = left_num < right_num
            elif op == ">":
                result = left_num > right_num
            elif op == "<=":
                result = left_num <= right_num
            elif op == ">=":
                result = left_num >= right_num
            else:
                result = False

            left = result  # For chained comparisons
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
        if var_name not in ["x", "y", "z", "time"]:  # Prevent overwriting constants
            self.vars[var_name] = value

    # Tokens
    def NUMBER(self, token):
        return float(token.value)

    def NAME(self, token):
        return str(token.value)

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
    return interpreter.return_value or "air"


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
