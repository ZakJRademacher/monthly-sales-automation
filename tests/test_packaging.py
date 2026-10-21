"""A rebuilt bundle must contain current docs, exact hashes, and no older ZIP."""
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
spec=importlib.util.spec_from_file_location("project_packager",ROOT/"tools/package_project.py")
packager=importlib.util.module_from_spec(spec)
spec.loader.exec_module(packager)


class PackageTests(unittest.TestCase):
    def test_rebuild_is_current_repeatable_and_excludes_old_archives(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            (root/"docs").mkdir()
            (root/"README.md").write_text("Current project")
            (root/"docs/PROJECT_GUIDE.md").write_text("Current operating guide")
            (root/"previous-release.zip").write_bytes(b"old archive")
            (root/".env").write_text("PRIVATE_SECRET")
            (root/"data").mkdir()
            (root/"data/review_notes.csv").write_text("PRIVATE_ANNOTATION")
            if packager.PROJECT!="monthly-sales-automation":
                (root/"results").mkdir()
                (root/"results/analysis.json").write_text('{"metrics":{}}')
            first=packager.build(root)
            first_bytes=Path(first["zip"]).read_bytes()
            (root/"docs/PROJECT_GUIDE.md").write_text("Revised operating guide")
            second=packager.build(root)
            self.assertNotEqual(first_bytes,Path(second["zip"]).read_bytes())
            third=packager.build(root)
            self.assertEqual(second["sha256"],third["sha256"])
            with zipfile.ZipFile(third["zip"]) as archive:
                names=archive.namelist()
                self.assertFalse(any(name.endswith(".zip") for name in names))
                self.assertFalse(any(name.endswith("/.env") for name in names))
                self.assertEqual(archive.read(packager.PREFIX+"/docs/PROJECT_GUIDE.md"),b"Revised operating guide")
                self.assertNotIn(b"PRIVATE_ANNOTATION",b"".join(archive.read(n) for n in names))
                manifest=json.loads(archive.read(packager.PREFIX+"/docs/package-manifest.json"))
                for record in manifest["files"]:
                    data=archive.read(packager.PREFIX+"/"+record["path"])
                    self.assertEqual(hashlib.sha256(data).hexdigest(),record["sha256"])
                    self.assertEqual(len(data),record["bytes"])


if __name__=="__main__":
    unittest.main()
