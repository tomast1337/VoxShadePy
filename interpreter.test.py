import unittest
from interpreter import (
    evaluate_voxel_shader,
)


class TestMathOperations(unittest.TestCase):
    def test_add_positive_numbers(self):
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
        self.assertEqual(result1, "air")
        self.assertEqual(result2, "water")

    def test_add_negative_numbers(self):
        program = """
        color = air;
        if (x < 0) {
            color = water;
        }
        """
        result1 = evaluate_voxel_shader(x=-1, y=2, z=3, time=0, program=program)
        # Should be 'water' since x < 0
        result2 = evaluate_voxel_shader(x=1, y=2, z=3, time=0, program=program)
        # Should be 'air' since x >= 0
        self.assertEqual(result1, "water")
        self.assertEqual(result2, "air")

    def test_nested_conditions(self):
        program = """
        color = air;
        if (x > 1) {
            if (y < 2) {
                color = water;
            } else {
                color = grass;
            }
        } else {
            color = dirt;
        }
        """
        result1 = evaluate_voxel_shader(x=2, y=1, z=3, time=0, program=program)
        # Should be 'water' since x > 1 and y < 2
        result2 = evaluate_voxel_shader(x=2, y=3, z=3, time=0, program=program)
        # Should be 'grass' since x > 1 and y >= 2
        result3 = evaluate_voxel_shader(x=0, y=2, z=3, time=0, program=program)
        # Should be 'dirt' since x <= 1
        self.assertEqual(result1, "water")
        self.assertEqual(result2, "grass")
        self.assertEqual(result3, "dirt")


if __name__ == "__main__":
    unittest.main()
