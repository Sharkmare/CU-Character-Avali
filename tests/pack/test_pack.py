import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PACK = os.path.join(ROOT, "pack")
LOADER_REPOSITORY = os.environ.get("CU_CHARACTERS_REPOSITORY", os.path.join(ROOT, "..", "CU Characters"))
PACK_CHECK_PROJECT = os.path.join(LOADER_REPOSITORY, "tools", "PackCheck")


class PackTests(unittest.TestCase):

    def test_pack_is_accepted_by_the_loader_without_problems(self):
        if not os.path.isdir(PACK_CHECK_PROJECT):
            self.fail("loader repository not found at %s (set CU_CHARACTERS_REPOSITORY)" % LOADER_REPOSITORY)
        result = subprocess.run(["dotnet", "run", "-c", "Release", "--project", PACK_CHECK_PROJECT, "--", PACK],
                                capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("avali/avary", result.stdout)
        self.assertIn("0 problem(s)", result.stdout)

    def test_skin_has_the_34_parts_the_loader_matches(self):
        body = os.path.join(PACK, "skins", "avary", "Body")
        names = [name for name in os.listdir(body) if name.endswith(".png")]
        self.assertEqual(34, len(names))
        for required in ("experimentHead.png", "experimentTail.png", "experimentEyeOpen.png"):
            self.assertIn(required, names)


if __name__ == "__main__":
    unittest.main()
