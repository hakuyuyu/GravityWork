"""
Unit tests for project scaffolding
"""

import unittest
import os
import subprocess

class TestProjectScaffolding(unittest.TestCase):
    def test_readme_exists(self):
        """Test that README.md exists"""
        self.assertTrue(os.path.exists("README.md"))

    def test_makefile_exists(self):
        """Test that Makefile exists"""
        self.assertTrue(os.path.exists("Makefile"))

    def test_readme_content(self):
        """Test that README.md has required sections"""
        with open("README.md", "r") as f:
            content = f.read()
            self.assertIn("Project Description", content)
            self.assertIn("Setup Instructions", content)
            self.assertIn("Development", content)

    def test_makefile_targets(self):
        """Test that Makefile has required targets"""
        result = subprocess.run(["make", "--dry-run"], capture_output=True, text=True)
        self.assertIn("setup", result.stdout)
        self.assertIn("test", result.stdout)
        self.assertIn("lint", result.stdout)
        self.assertIn("clean", result.stdout)

if __name__ == "__main__":
    unittest.main()
