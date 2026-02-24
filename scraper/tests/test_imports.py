
import importlib
import pkgutil
import unittest
import scraper

class TestImports(unittest.TestCase):
    def test_imports(self):
        """Recursively import all modules in scraper package."""
        package = scraper
        prefix = package.__name__ + "."

        for _, name, _ in pkgutil.walk_packages(package.__path__, prefix):
            with self.subTest(module=name):
                try:
                    importlib.import_module(name)
                except Exception as e:
                    self.fail(f"Failed to import {name}: {e}")

if __name__ == "__main__":
    unittest.main()
