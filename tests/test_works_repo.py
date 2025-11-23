import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from bcut.services.works_repo import (
    load_works_info,
    save_works_info,
    add_work,
    update_work,
    remove_work,
    find_by_id,
    find_by_draft,
)
from bcut.models.works import WorksInfo


class TestWorksRepo(unittest.TestCase):
    def test_crud(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp) / "Bcut Drafts"
            base.mkdir(parents=True, exist_ok=True)
            wp = base / "worksInfo.json"

            info = load_works_info(wp)
            self.assertEqual(len(info.worksInfos), 0)

            w = add_work(wp, draftId="DRAFT-1", name="作品A", duration=1000)
            self.assertTrue(find_by_id(wp, w.id))
            self.assertEqual(len(find_by_draft(wp, "DRAFT-1")), 1)

            w2 = update_work(wp, w.id, name="作品A-改", status=2)
            self.assertIsNotNone(w2)
            self.assertEqual(w2.name, "作品A-改")
            self.assertEqual(w2.status, 2)

            ok = remove_work(wp, w.id)
            self.assertTrue(ok)
            self.assertIsNone(find_by_id(wp, w.id))

            # save empty structure and reload
            save_works_info(WorksInfo(), wp)
            re = load_works_info(wp)
            self.assertEqual(len(re.worksInfos), 0)


if __name__ == "__main__":
    unittest.main()