from __future__ import annotations

import importlib
import pkgutil
import unittest
import scraper

class TestImports(unittest.TestCase):
    def test_imports(self) -> None:
        """Recursively import all modules in scraper package."""
        package = scraper
        prefix = package.__name__ + "."

        for _, name, _ in pkgutil.walk_packages(package.__path__, prefix):
            with self.subTest(module=name):
                try:
                    importlib.import_module(name)
                except Exception as e:
                    # Catch all exceptions to ensure we report which module failed to import
                    # instead of crashing the test runner completely.
                    self.fail(f"Failed to import {name}: {e}")

if __name__ == "__main__":
    unittest.main()
