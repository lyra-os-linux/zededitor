from __future__ import annotations

import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ZedPackagingTests(unittest.TestCase):
    def test_sources_are_https_checksum_pinned_and_match_spec_version(self) -> None:
        root = ET.parse(ROOT / "_service").getroot()
        services = root.findall("service")
        downloads = [service for service in services if service.get("name") == "download_url"]
        verifiers = [service for service in services if service.get("name") == "verify_file"]
        self.assertEqual(len(downloads), 3)
        self.assertEqual(len(verifiers), 3)

        spec = (ROOT / "zed.spec").read_text(encoding="utf-8")
        version = re.search(r"^Version:\s+(\S+)$", spec, re.MULTILINE)
        self.assertIsNotNone(version)
        tag = f"v{version.group(1)}"
        expected_files = {
            "zed-linux-x86_64.tar.gz", "LICENSE-GPL", "LICENSE-APACHE"
        }
        downloaded_files: set[str] = set()
        for service in downloads:
            params = {param.get("name"): (param.text or "") for param in service}
            self.assertEqual(params["protocol"], "https")
            self.assertIn(params["host"], {"github.com", "raw.githubusercontent.com"})
            self.assertIn(f"/{tag}/", params["path"])
            self.assertNotIn("latest", params["path"].lower())
            downloaded_files.add(Path(params["path"]).name)
        self.assertEqual(downloaded_files, expected_files)

        verified_files: set[str] = set()
        for service in verifiers:
            params = {param.get("name"): (param.text or "") for param in service}
            self.assertEqual(params["verifier"], "sha256")
            self.assertRegex(params["checksum"], r"^[0-9a-f]{64}$")
            verified_files.add(params["file"].removeprefix("_service:download_url:"))
        self.assertEqual(verified_files, expected_files)

    def test_licenses_and_desktop_file_are_packaging_gates(self) -> None:
        spec = (ROOT / "zed.spec").read_text(encoding="utf-8")
        self.assertRegex(spec, r"(?m)^License:\s+GPL-3\.0-only AND Apache-2\.0$")
        self.assertIn("%license LICENSE-GPL LICENSE-APACHE", spec)
        self.assertIn("desktop-file-validate", spec)
        self.assertIn("grep -qxF 'Exec=zed %U'", spec)

    def test_launcher_redirects_updates_to_zypper(self) -> None:
        spec = (ROOT / "zed.spec").read_text(encoding="utf-8")
        launcher = (ROOT / "zed-launcher").read_text(encoding="utf-8")
        self.assertIn("ZED_UPDATE_EXPLANATION", spec)
        self.assertIn("ZED_UPDATE_EXPLANATION", launcher)
        self.assertIn("Zypper", launcher)
        self.assertIn('exec /usr/libexec/zed/bin/zed "$@"', launcher)

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
