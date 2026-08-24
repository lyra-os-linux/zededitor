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

    def test_bundled_libraries_excluded_from_auto_requires(self) -> None:
        # Without this, RPM's auto-Requires scans the bundled private
        # libraries (e.g. libffi.so.7) and demands a matching system
        # library, even though they are only ever loaded via Zed's own
        # $ORIGIN-relative RPATH.
        spec = (ROOT / "zed.spec").read_text(encoding="utf-8")
        self.assertIn("__requires_exclude_from", spec)
        for line in spec.splitlines():
            if line.startswith("%global __requires_exclude_from"):
                self.assertIn("_libexecdir}/zed/lib/", line)
                break
        else:
            self.fail("no __requires_exclude_from global found in zed.spec")


if __name__ == "__main__":
    unittest.main()
