import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from bcut.services.draft_repo import create_draft, build_drafts_index


class TestCreateDraft(unittest.TestCase):
    def test_create_draft_basic(self):
        with TemporaryDirectory() as tmp:
            base_dir = Path(tmp) / "Bcut Drafts"
            result = create_draft(
                base_dir=base_dir,
                name="测试草稿",
            )
            draft_id = result["draft_id"]
            folder = Path(result["folder"])
            bjson = Path(result["bjson"])

            self.assertTrue(folder.exists())
            self.assertTrue(bjson.exists())
            self.assertGreater(bjson.stat().st_size, 0)

            draft_info = base_dir / "draftInfo.json"
            self.assertTrue(draft_info.exists())
            data = json.loads(draft_info.read_text(encoding="utf-8"))
            ids = [d["id"] for d in data.get("draftInfos", [])]
            names = {d["id"]: d["name"] for d in data.get("draftInfos", [])}
            self.assertIn(draft_id, ids)
            self.assertEqual(names[draft_id], "测试草稿")

            index = build_drafts_index(base_dir)
            self.assertEqual(len(index), 1)
            self.assertEqual(index[0]["folder_id"], draft_id)
            self.assertIn(str(bjson), index[0]["bjson_files"])


if __name__ == "__main__":
    unittest.main()