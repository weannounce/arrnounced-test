#!/usr/bin/env python3

import unittest
import sys
#import coverage

#sys.path.append("helpers/")

#cov = coverage.coverage(
#    branch=True, include="src/*", omit=["*/__init__.py", "*/config/*"]
#)

if __name__ == "__main__":
    #cov.start()

    suite = unittest.TestLoader().discover("tests", pattern="single*")
    result = unittest.TextTestRunner().run(suite)

    #cov.stop()
    #cov.save()
    #cov.report()
    #cov.html_report(directory="./coverage")
    #cov.erase

    sys.exit(0 if result.wasSuccessful() else 1)
