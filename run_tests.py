#!/usr/bin/env python3

import unittest
import sys

if __name__ == "__main__":
    suite = unittest.TestLoader().discover("tests", pattern="test_*.py")
    result = unittest.TextTestRunner().run(suite)

    sys.exit(0 if result.wasSuccessful() else 1)
