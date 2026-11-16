import json
import tempfile
import unittest
from pathlib import Path
from scripts.video_factory import validate, build

EXAMPLE = Path(__file__).parents[1] / "templates" / "video_job.example.json"

class VideoFactoryTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_example_passes(self):
        self.assertEqual(validate(self.data), [])

    def test_unapproved_product_is_blocked(self):
        self.data["product"]["approval_status"] = "RESEARCH"
        self.assertTrue(any("APPROVED_FOR_CONTENT" in x for x in validate(self.data)))

    def test_pending_asset_is_blocked(self):
        self.data["assets"][0]["rights_status"] = "pending"
        self.assertTrue(any("not cleared" in x for x in validate(self.data)))

    def test_pack_contains_nine_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = build(self.data, Path(tmp))
            self.assertEqual(len(list(result.iterdir())), 9)
            meta = json.loads((result / "08_publish_metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["publishing_status"], "not_published")

if __name__ == "__main__":
    unittest.main()
