#!/usr/bin/env python3
"""
Unit/E2E Test Suite for Playwright Screen Capture & UI Verification
Project: Bend DevOps Guardian
"""

import unittest
from pathlib import Path
from tests.e2e.capture_screenshots import capture_all_screens, SCREENSHOTS_DIR

class TestPlaywrightScreenshots(unittest.TestCase):
    def test_capture_all_screens_and_verify_files(self):
        """Executes full Playwright screenshot capture and verifies all files are generated."""
        captured = capture_all_screens()
        self.assertGreaterEqual(len(captured), 15, "Expected at least 15 captured screens")

        for item in captured:
            file_path = SCREENSHOTS_DIR / item["file"]
            self.assertTrue(file_path.exists(), f"Screenshot {item['file']} does not exist")
            file_size = file_path.stat().st_size
            self.assertGreater(file_size, 10000, f"Screenshot {item['file']} is unexpectedly small ({file_size} bytes)")

        readme_path = SCREENSHOTS_DIR / "README.md"
        self.assertTrue(readme_path.exists(), "README.md catalog was not created")
        readme_text = readme_path.read_text(encoding="utf-8")
        self.assertIn("Bend DevOps Guardian", readme_text)

if __name__ == "__main__":
    unittest.main()
