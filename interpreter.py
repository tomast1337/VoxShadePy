from lark import Lark, Tree
from lark.visitors import Interpreter
import numpy as np
from noise import snoise4

with open("voxel_grammar.lark") as f:
    grammar = f.read()

parser = Lark(grammar, parser="lalr", start="start")


class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value


class VoxelShadeInterpreter(Interpreter):

    def __init__(self, x, y, z, time):
        self.global_vars = {
            "x": x,
            "y": y,
            "z": z,
            "air": "air",
            "stone": "stone",
            "water": "water",
            "grass": "grass",
            "crystal": "crystal",
            "sand": "sand",
            "wood": "wood",
            "metal": "metal",
            "lava": "lava",
            "ice": "ice",
            "dirt": "dirt",
            "snow": "snow",
            "cloud": "cloud",
            "glass": "glass",
            "brick": "brick",
            "obsidian": "obsidian",
            "time": time,
        }
        self.protected_vars = [
            "x",
            "y",
            "z",
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
            "time",
        ]
        self.vars_stack = [self.global_vars]
        self.functions = {}
        self.result = None

    def push_scope(self):
        self.vars_stack.append({})

    def pop_scope(self):
        self.vars_stack.pop()

    def current_scope(self):
        return self.vars_stack[-1]

    def get_var(self, name):
        # search from top scope down
        for scope in reversed(self.vars_stack):
            if name in scope:
                return scope[name]
        return 0

    def set_var(self, name, value):
        if name in self.protected_vars:
            raise Exception(f"Cannot assign to protected variable '{name}'")
        self.current_scope()[name] = value
        if name == "color":
            self.result = value

    def assignment(self, tree):
        var = tree.children[0].value
        value = self.visit(tree.children[1])
        self.set_var(var, value)

    def block(self, tree):
        result = None
        for stmt in tree.children:
            result = self.visit(stmt)
        return result

    def if_statement(self, tree):
        cond = self.visit(tree.children[0])
        then_stmt = tree.children[1]
        else_stmt = tree.children[2] if len(tree.children) > 2 else None
        if cond:
            return self.visit(then_stmt)
        elif else_stmt is not None:
            return self.visit(else_stmt)

    def func_decl(self, tree):
        func_name = tree.children[0].value
        params_tree = tree.children[1] if len(tree.children) > 2 else None
        block_tree = tree.children[-1]

        params = []
        if params_tree is not None and params_tree.data == "param_list":
            params = [p.value for p in params_tree.children]
        elif (
            params_tree is not None
            and isinstance(params_tree, Tree)
            and params_tree.data != "block"
        ):
            # single param maybe
            params = [params_tree.children[0].value]

        self.functions[func_name] = (params, block_tree)

    def return_statement(self, tree):
        value = self.visit(tree.children[0])
        raise ReturnValue(value)

    def func_call(self, tree):
        func_name = tree.children[0].value
        args = [self.visit(arg) for arg in tree.children[1:]]

        # Check builtin functions first
        if func_name == "sin":
            if len(args) != 1:
                raise Exception("sin() takes exactly 1 argument")
            return np.sin(args[0])
        elif func_name == "cos":
            if len(args) != 1:
                raise Exception("cos() takes exactly 1 argument")
            return np.cos(args[0])
        elif func_name == "noise":
            if len(args) != 4:
                raise Exception("noise() takes exactly 4 arguments: x,y,z,t")
            return snoise4(*args)

        # User-defined function
        if func_name not in self.functions:
            raise Exception(f"Unknown function: {func_name}")

        params, block_tree = self.functions[func_name]
        if len(params) != len(args):
            raise Exception(
                f"Function {func_name} expects {len(params)} args, got {len(args)}"
            )

        self.push_scope()
        for p, a in zip(params, args):
            self.set_var(p, a)

        try:
            ret = self.visit(block_tree)
        except ReturnValue as r:
            self.pop_scope()
            return r.value

        self.pop_scope()
        return ret

    def vec3(self, tree):
        return tuple(self.visit(child) for child in tree.children)

    def add(self, tree):
        return self.visit(tree.children[0]) + self.visit(tree.children[1])

    def sub(self, tree):
        return self.visit(tree.children[0]) - self.visit(tree.children[1])

    def mul(self, tree):
        return self.visit(tree.children[0]) * self.visit(tree.children[1])

    def div(self, tree):
        return self.visit(tree.children[0]) / self.visit(tree.children[1])

    def number(self, tree):
        return float(tree.children[0])

    def var(self, tree):
        name = tree.children[0].value
        return self.get_var(name)

    def gt(self, tree):
        return self.visit(tree.children[0]) > self.visit(tree.children[1])

    def lt(self, tree):
        return self.visit(tree.children[0]) < self.visit(tree.children[1])

    def ge(self, tree):
        return self.visit(tree.children[0]) >= self.visit(tree.children[1])

    def le(self, tree):
        return self.visit(tree.children[0]) <= self.visit(tree.children[1])

    def eq(self, tree):
        return self.visit(tree.children[0]) == self.visit(tree.children[1])

    def ne(self, tree):
        return self.visit(tree.children[0]) != self.visit(tree.children[1])

    def or_(self, tree):
        left = self.visit(tree.children[0])
        right = self.visit(tree.children[1])
        return left or right

    def and_(self, tree):
        left = self.visit(tree.children[0])
        right = self.visit(tree.children[1])
        return left and right

    def not_(self, tree):
        val = self.visit(tree.children[0])
        return not val


def evaluate_voxel_shader(x, y, z, time, program):
    tree = parser.parse(program)
    interpreter = VoxelShadeInterpreter(x, y, z, time)
    interpreter.visit(tree)
    return interpreter.result


if __name__ == "__main__":
    # Example usage
    program = """
    color = air;
    if (x > 1) {
        color = water;
    }
    """
    result1 = evaluate_voxel_shader(
        x=1, y=2, z=3, time=0, program=program
    )  # Should be 'air'
    result2 = evaluate_voxel_shader(
        x=2, y=2, z=3, time=0, program=program
    )  # Should be 'water'
    print(f"Result for (1, 2, 3) time = 0: {result1}, Expected: 'air'")
    print(f"Result for (2, 2, 3) time = 0: {result2}, Expected: 'water'")
