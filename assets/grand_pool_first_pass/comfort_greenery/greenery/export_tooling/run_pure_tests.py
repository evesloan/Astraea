"""Seventeen pure tests; no Blender, export or engine launch."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import unittest
def suite():return unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(n) for n in ['test_predicates','test_glb_equivalence','test_reproducibility_guards'])
if __name__=='__main__':
    tests=suite();assert tests.countTestCases()==17
    result=unittest.TextTestRunner(verbosity=2).run(tests);sys.exit(0 if result.wasSuccessful() else 1)
