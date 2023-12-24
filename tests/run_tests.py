import sys
import logging
import unittest
import tests.test_connections
import tests.test_routers


if __name__ == "__main__":
    logging.basicConfig( stream=sys.stderr )
    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(loader.loadTestsFromModule(tests.test_connections))
    runner.run(loader.loadTestsFromModule(tests.test_routers))