#!/usr/bin/env python3

import argparse
import unittest
import sys

from helpers import config

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Arrnounced integration tests")
    parser.add_argument(
        "-d",
        "--docker",
        type=str,
        help="Run docker image",
        default=None,
    )
    parser.add_argument(
        "test", type=str, help="Which tests to run", nargs="?", default="*"
    )

    try:
        args = parser.parse_args()
    except Exception as e:
        print(e)
        sys.exit(1)

    config.docker = args.docker

    suite = unittest.TestLoader().discover(
        start_dir="tests", pattern=f"test_{args.test}.py"
    )
    result = unittest.TextTestRunner().run(suite)

    sys.exit(0 if result.wasSuccessful() else 1)
