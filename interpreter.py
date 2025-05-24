from lark import Lark, Transformer
import numpy as np

with open("voxel_grammar.lark") as f:
    GRAMMAR = f.read()


class ReturnSignal(Exception):
    """Signal to break out of execution when return is encountered"""

    pass


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
        """Handle regular variables"""
        if not args:
            return 0.0
        name = str(args[0])
        if name in MATERIALS:
            # This shouldn't happen with the updated grammar
            print(f"Warning: Material '{name}' processed as variable")
            return name
        print(f"Variable lookup: {name} -> {self.vars.get(name, 0.0)}")
        return self.vars.get(name, 0.0)

    def material(self, args):
        """Handle material tokens directly"""
        material_name = str(args[0])
        print(f"Material received: {material_name}")
        return material_name

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
        if len(args) != 2:
            return
        condition, block = args
        if condition:
            # Execute the block and capture any return value
            self.transform(block)

    def block(self, args):
        """Execute block statements with return tracking"""
        for stmt in args:
            self.transform(stmt)
            if self.should_return:
                break

    def return_stmt(self, args):
        """Process return statements with proper type handling"""
        if not args:
            self.return_value = "air"
            return

        return_value = args[0]
        print(f"Raw return value: {return_value} (type: {type(return_value)})")

        # Handle all string returns (both materials and other strings)
        if isinstance(return_value, str):
            self.return_value = return_value
        else:
            # Convert numbers to strings
            self.return_value = str(return_value)

        print(f"Final return value set to: {self.return_value}")
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

    def transform(self, tree):
        print(f"Transforming: {tree}")
        return super().transform(tree)


def run_shader(code, x: float = 0, y: float = 0, z: float = 0, time: float = 0):
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
