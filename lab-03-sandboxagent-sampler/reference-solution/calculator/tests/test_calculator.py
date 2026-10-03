import unittest

from calculator import add, divide, multiply, subtract


class CalculatorTests(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

    def test_subtract(self):
        self.assertEqual(subtract(7, 4), 3)

    def test_multiply(self):
        # This is the exercise's single intentional failure.
        self.assertEqual(multiply(7, 4), 28)

    def test_divide(self):
        self.assertEqual(divide(20, 4), 5)


if __name__ == "__main__":
    unittest.main()
