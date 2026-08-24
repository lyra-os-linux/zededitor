from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ZedPackagingTests(unittest.TestCase):
    def test_launcher_redirects_updates_to_zypper(self) -> None:
        spec = (ROOT / "zed.spec").read_text(encoding="utf-8")
        launcher = (ROOT / "zed-launcher").read_text(encoding="utf-8")
        self.assertIn("ZED_UPDATE_EXPLANATION", spec)
        self.assertIn("ZED_UPDATE_EXPLANATION", launcher)
        self.assertIn("Zypper", launcher)

    def test_bundled_libraries_excluded_from_auto_provides(self) -> None:
        spec = (ROOT / "zed.spec").read_text(encoding="utf-8")
        self.assertIn("__provides_exclude_from", spec)
        self.assertIn("_libexecdir}/zed/lib/", spec)


if __name__ == "__main__":
    unittest.main()
