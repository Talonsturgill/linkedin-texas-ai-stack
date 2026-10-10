import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import check_skill
import smoke_test


class SkillTests(unittest.TestCase):
    def validate(self, text):
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp) / 'SKILL.md').write_text(text)
            return check_skill.validate_skill(temp)[0]

    def test_valid_skill_and_literal_example(self):
        self.assertTrue(self.validate('---\nname: example\ndescription: A useful skill\n---\n'
                                      '```\n[TODO: example syntax]\n```\n'))

    def test_invalid_frontmatter(self):
        for front in ('[]', 'name: Bad_Name\ndescription: Valid',
                      'name: example\ndescription: ""', 'name: example\ndescription: 12',
                      'name: example\ndescription: Good\nunrecognized: yes'):
            with self.subTest(front=front):
                self.assertFalse(self.validate('---\n' + front + '\n---\n'))

    def test_placeholder_outside_fence_fails(self):
        self.assertFalse(self.validate('---\nname: example\ndescription: Good\n---\n'
                                       '```\ncode\n```\n[TODO: write instructions]\n'))


class SmokeSafetyTests(unittest.TestCase):
    def test_rejects_production_and_parent_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for value in ('out', '.', '.local', '../outside'):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    smoke_test.destination(root, value)
            self.assertEqual(smoke_test.destination(root, '.local/new'), root.resolve() / '.local/new')

    def test_existing_fixture_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / '.local/existing').mkdir(parents=True)
            with self.assertRaises(ValueError):
                smoke_test.destination(root, '.local/existing')

    def test_symlink_cannot_escape_repository(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as outside:
            root = Path(temp)
            (root / '.local').symlink_to(outside)
            with self.assertRaises(ValueError):
                smoke_test.destination(root, '.local/new')
