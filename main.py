from interpreter import run_shader


def main():
    code = """
if (x == 8.0) {
    return grass;
}
return air;
"""
    result = run_shader(code, x=8, y=2, z=3, time=4)
    print(f"Result: {result}")


if __name__ == "__main__":
    main()
