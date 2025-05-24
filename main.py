from interpreter import run_shader


def test_comparison():
    code = """
    if (x == 8.0) {
        return grass;
    }
    return air;
    """
    result = run_shader(code, x=8, y=2, z=3, time=4)
    assert result == "grass", f"Expected grass, got {result}"

    result = run_shader(code, x=7, y=2, z=3, time=4)
    assert result == "air", f"Expected grass, got {result}"

    print("Test passed!")


if __name__ == "__main__":
    test_comparison()
