import unittest
from pathlib import Path

from tristan.atlas_federation import compile_atlas_federation
from tristan.registry import Registry


ROOT = Path(__file__).resolve().parents[1]


class AtlasFederationR7Tests(unittest.TestCase):
    def test_compiles_bounded_top_projections(self):
        reg = Registry.load(ROOT / "registry/objects.jsonl")
        receipt = compile_atlas_federation("fuse atlas tfuga hgfm jarvis omega", reg)
        self.assertEqual(receipt.schema_version, "jarvis-atlas-federation-r7")
        self.assertLessEqual(len(receipt.top16), 16)
        self.assertLessEqual(len(receipt.top64), 64)
        self.assertLessEqual(len(receipt.top256), 256)
        self.assertTrue(receipt.next_action.startswith("M-ATLAS-"))
        self.assertFalse(receipt.scientific_pass)
        self.assertFalse(receipt.authority_granted)

    def test_private_source_is_descriptor_only(self):
        reg = Registry.load(ROOT / "registry/objects.jsonl")
        receipt = compile_atlas_federation("fuse everything", reg)
        private_sources = [
            source for source in receipt.sources
            if source["visibility"] == "private"
        ]
        self.assertTrue(private_sources)
        self.assertTrue(
            all("url" not in source and "content" not in source for source in private_sources)
        )

    def test_duplicate_families_generate_canonicalization_missions(self):
        reg = Registry.load(ROOT / "registry/objects.jsonl")
        receipt = compile_atlas_federation("fuse everything", reg)
        self.assertTrue(any(
            mission["transformation"] == "CANONICALIZE_DUPLICATE_FAMILY"
            for mission in receipt.missions
        ))
        self.assertIn("AtlasProjection != ScientificRanking", receipt.boundaries)


if __name__ == "__main__":
    unittest.main()
