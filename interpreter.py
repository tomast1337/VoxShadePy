from lark import Transformer, Lark
import math

MATERIALS = {"air", "stone", "water", "grass", "crystal"}


class EvalError(Exception):
    pass


class EvalTransformer(Transformer):
    def __init__(self, env):
        super().__init__()
        self.env = env  # variable context
        self.returned = None

    def number(self, token):
        return float(token)

    def var(self, token):
        name = str(token)
        if name in self.env:
            return self.env[name]
        elif name in MATERIALS:
            return name
        raise EvalError(f"Unknown variable: {name}")

    def add(self, items):
        return items[0] + items[1]

    def sub(self, items):
        return items[0] - items[1]

    def mul(self, items):
        return items[0] * items[1]

    def div(self, items):
        return items[0] / items[1]

    def compare(self, items):
        if len(items) == 1:
            return items[0]
        left, op_token, right = items
        op = str(op_token)
        try:
            return {
                "==": left == right,
                "!=": left != right,
                "<": left < right,
                ">": left > right,
                "<=": left <= right,
                ">=": left >= right,
            }[op]
        except KeyError:
            raise EvalError(f"Unknown comparison operator: {op}")

    def func_call(self, items):
        name = str(items[0])
        args = items[1:]
        if name in {"sin", "cos", "abs", "floor"}:
            return getattr(math, name)(*args)
        raise EvalError(f"Unknown function: {name}")

    def assign_stmt(self, items):
        name = str(items[0])
        value = items[1]
        self.env[name] = value

    def expr_stmt(self, items):
        pass  # Evaluate but discard

    def return_stmt(self, items):
        self.returned = items[0]

    def if_stmt(self, items):
        condition = items[0]
        block = items[1]
        if condition:
            for stmt in block:
                if self.returned is not None:
                    break

    def block(self, items):
        return items

    def start(self, items):
        return items


with open("voxel_grammar.lark") as f:
    grammar = f.read()

parser = Lark(grammar, parser="lalr")


def run(code, x, y, z, time):
    tree = parser.parse(code)
    env = dict(x=x, y=y, z=z, time=time)
    evaluator = EvalTransformer(env)
    evaluator.transform(tree)
    return evaluator.returned or "air"
