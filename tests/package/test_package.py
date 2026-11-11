import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import sys
import tempfile
import unittest
import zipfile

TOOLS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools")
sys.path.insert(0, TOOLS)

import build_package as package  # noqa: E402

BANNED_NAME_PARTS = (".pdb", ".log", ".cs", ".py", "test", "debug", ".dll")
TEXT_SUFFIXES = (".txt", ".md", ".json")
VERSION = "9.9.9"


TOGETHER_BASE_LINK = "https://github.com/Sharkmare/casualties-together"
ALLOWED_LINK = TOGETHER_BASE_LINK + "/tree/characters"
PORTAL_LINK = "https://skin.cat-bot.de/?skinid=200"
LOADER_LINK = "https://github.com/Sharkmare/CasualtiesCharacters-loader"
ALLOWED_URLS = (ALLOWED_LINK, PORTAL_LINK, LOADER_LINK)
ALLOWED_REPOSITORY_LINKS = (ALLOWED_LINK, LOADER_LINK)
LICENCE_WORDING = r"licen[cs]e|reuse"


def foreign_repository_text(text):
    without_allowed = text
    for link in ALLOWED_REPOSITORY_LINKS:
        without_allowed = re.sub(re.escape(link) + r"(?![\w/.-])", "", without_allowed)
    return re.findall(r"github[^\s]*", without_allowed, flags=re.IGNORECASE)


def unexpected_urls(text):
    found = [url.rstrip(".,;)") for url in re.findall(r"https?://[^\s`\"']+", text)]
    return [url for url in found if url not in ALLOWED_URLS]


def licence_wording(text):
    return re.findall(LICENCE_WORDING, text, flags=re.IGNORECASE)


def build_suffixes(text):
    return re.findall(r"\d\+\d+", text)


def private_script():
    override = os.environ.get("CU_RELEASE_RULES")
    candidates = [pathlib.Path(override)] if override else []
    candidates += [sibling / "release_rules" / "banned_words.txt" for sibling in pathlib.Path(__file__).resolve().parents[3].iterdir()]
    for candidate in candidates:
        rules = candidate / "banned_words.txt" if candidate.is_dir() else candidate
        script = rules.parent.parent / "tools" / "check_release_text.py"
        if rules.is_file() and script.is_file():
            return script
    return None


def private_wording_problems(target):
    script = private_script()
    if script is None:
        print("internal wording check skipped (private rules not found)")
        return []
    result = subprocess.run([sys.executable, "-I", str(script), str(target)], capture_output=True, text=True)
    return [] if result.returncode == 0 else result.stdout.splitlines()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def source_png_names():
    folder = os.path.join(package.PACK_DIRECTORY, "skins", "avary", "Body")
    return sorted(os.listdir(folder))


def expected_entries():
    root = package.PACK_FOLDER + "/"
    names = {package.INSTALL_ENTRY, package.CREDITS_ENTRY, root + "pack.json", root + "characters/avali_avary.json"}
    names |= {root + "skins/avary/Body/" + name for name in source_png_names()}
    return names


class PackageTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.workdir = tempfile.TemporaryDirectory()
        cls.zip_path = os.path.join(cls.workdir.name, "out", package.package_file_name(VERSION))
        package.build(cls.zip_path, VERSION)
        with zipfile.ZipFile(cls.zip_path) as archive:
            cls.entries = {name: archive.read(name) for name in archive.namelist()}

    @classmethod
    def tearDownClass(cls):
        cls.workdir.cleanup()

    def test_file_name_is_the_product_and_version(self):
        self.assertEqual("CasualtiesCharacters-Avali-9.9.9.zip", os.path.basename(self.zip_path))

    def test_contains_exactly_the_expected_entries(self):
        self.assertEqual(expected_entries(), set(self.entries))
        self.assertEqual(34, len(source_png_names()))

    def test_unzipped_files_equal_the_sources(self):
        target = os.path.join(self.workdir.name, "game")
        with zipfile.ZipFile(self.zip_path) as archive:
            archive.extractall(target)
        for name in sorted(self.entries):
            if name == package.INSTALL_ENTRY:
                continue
            source = package.CREDITS_SOURCE if name == package.CREDITS_ENTRY else os.path.join(
                package.PACK_DIRECTORY, *name[len(package.PACK_FOLDER) + 1:].split("/"))
            with open(source, "rb") as original, open(os.path.join(target, *name.split("/")), "rb") as unzipped:
                self.assertEqual(sha256(original.read()), sha256(unzipped.read()), name)

    def test_png_signatures(self):
        for name, data in self.entries.items():
            if name.endswith(".png"):
                self.assertTrue(data.startswith(package.PNG_SIGNATURE), name)

    def test_only_the_avary_skin_is_bundled(self):
        folders = {name.split("/")[4] for name in self.entries if "/skins/" in name}
        self.assertEqual({"avary"}, folders)

    def test_no_code_ships(self):
        for name in self.entries:
            self.assertFalse(name.lower().endswith((".dll", ".pdb", ".cs", ".py")), name)

    def test_names_have_no_debug_or_source_parts(self):
        names = list(self.entries) + [os.path.basename(self.zip_path)]
        for name in names:
            lowered = name.lower().replace("casualtiescharacters", "")
            for part in BANNED_NAME_PARTS:
                self.assertNotIn(part, lowered, name)

    def test_private_wording_check_passes_on_the_built_package(self):
        self.assertEqual([], private_wording_problems(self.zip_path))

    def test_readme_ends_with_the_development_line(self):
        with open(os.path.join(package.ROOT, "README.md"), encoding="utf-8") as handle:
            text = handle.read()
        self.assertEqual("Build, test and design notes are in `docs/dev/`.", text.strip().splitlines()[-1])

    def test_private_wording_check_passes_on_the_repository(self):
        self.assertEqual([], private_wording_problems(package.ROOT))

    def test_install_text_has_the_required_sections(self):
        text = self.entries[package.INSTALL_ENTRY].decode("utf-8").replace("\r\n", "\n")
        for needle in ("CasualtiesCharacters-Avali 9.9.9", "BepInEx " + package.BEPINEX_VERSION,
                       "The %s from %s, version %s or newer" % (package.LOADER_NAME, LOADER_LINK, package.LOADER_MIN_VERSION),
                       "a %s, built from the source at %s" % (package.TOGETHER_NAME, ALLOWED_LINK),
                       "the %s branch is the one with the extra character support" % package.TOGETHER_BRANCH,
                       "Building section", "installed by every player",
                       "Install", "Use", "Known limitations", "Credits", "CREDITS.md", "paili16", PORTAL_LINK,
                       "Singleplayer works with the loader alone", "Avary is not available\n  in multiplayer and everything else stays vanilla"):
            self.assertIn(needle, text)

    def test_credits_keep_the_skin_chain(self):
        text = self.entries[package.CREDITS_ENTRY].decode("utf-8")
        for needle in ("paili16", PORTAL_LINK):
            self.assertIn(needle, text)

    def test_loader_requirement_matches_the_pack_manifest(self):
        manifest = json.loads(self.entries[package.PACK_FOLDER + "/pack.json"].decode("utf-8"))
        self.assertEqual(package.LOADER_MIN_VERSION, manifest["minLoader"])
        self.assertEqual("avali", manifest["id"])
        self.assertEqual(package.read_version(), manifest["version"])

    def test_the_one_allowed_link_is_the_constant_and_appears_once_in_install_text_and_readme(self):
        self.assertEqual(ALLOWED_LINK, package.TOGETHER_URL)
        self.assertEqual(1, self.entries[package.INSTALL_ENTRY].decode("utf-8").count(ALLOWED_LINK))
        with open(os.path.join(package.ROOT, "README.md"), encoding="utf-8") as handle:
            self.assertEqual(1, handle.read().count(ALLOWED_LINK))

    def test_no_other_repository_link_or_github_text_ships(self):
        for name, data in self.entries.items():
            self.assertEqual([], foreign_repository_text(name), name)
            if name.lower().endswith(TEXT_SUFFIXES):
                self.assertEqual([], foreign_repository_text(data.decode("utf-8")), name)
        with open(os.path.join(package.ROOT, "README.md"), encoding="utf-8") as handle:
            self.assertEqual([], foreign_repository_text(handle.read()), "README.md")

    def test_install_text_and_readme_offer_no_download(self):
        with open(os.path.join(package.ROOT, "README.md"), encoding="utf-8") as handle:
            readme = handle.read()
        for text in (self.entries[package.INSTALL_ENTRY].decode("utf-8"), readme):
            self.assertNotIn("download:", text.lower())
            self.assertNotIn("release page", text.lower())
        self.assertIn("No prebuilt download is offered", readme)

    def test_no_build_suffix_ships(self):
        with open(os.path.join(package.ROOT, "README.md"), encoding="utf-8") as handle:
            readme = handle.read()
        texts = [data.decode("utf-8") for name, data in self.entries.items() if name.lower().endswith(TEXT_SUFFIXES)] + [readme]
        for text in texts:
            self.assertEqual([], build_suffixes(text))

    def test_the_suffix_checker_can_fail(self):
        self.assertEqual([], build_suffixes("version 5.4.1 and loader 0.2.0"))
        self.assertTrue(build_suffixes("version 5.4.1+1"))
        self.assertTrue(build_suffixes("5.4.1+23"))
        self.assertTrue(build_suffixes("build 7+2 or later"))

    def test_author_and_portal_link_are_in_credits_readme_and_install_text(self):
        with open(os.path.join(package.ROOT, "README.md"), encoding="utf-8") as handle:
            readme = handle.read()
        for text in (self.entries[package.CREDITS_ENTRY].decode("utf-8"), readme, self.entries[package.INSTALL_ENTRY].decode("utf-8")):
            self.assertIn("paili16", text)
            self.assertIn(PORTAL_LINK, text)

    def test_only_the_allowed_urls_ship(self):
        with open(os.path.join(package.ROOT, "README.md"), encoding="utf-8") as handle:
            readme = handle.read()
        texts = [data.decode("utf-8") for name, data in self.entries.items() if name.lower().endswith(TEXT_SUFFIXES)] + [readme]
        for text in texts:
            self.assertEqual([], unexpected_urls(text))

    def test_each_allowed_url_appears_only_where_intended(self):
        with open(os.path.join(package.ROOT, "README.md"), encoding="utf-8") as handle:
            readme = handle.read()
        install = self.entries[package.INSTALL_ENTRY].decode("utf-8")
        credits = self.entries[package.CREDITS_ENTRY].decode("utf-8")
        expected = {
            ALLOWED_LINK: (1, 1, 0),
            LOADER_LINK: (1, 1, 0),
            PORTAL_LINK: (1, 1, 1),
        }
        for link, (in_install, in_readme, in_credits) in expected.items():
            self.assertEqual(in_install, install.count(link), "install " + link)
            self.assertEqual(in_readme, readme.count(link), "readme " + link)
            self.assertEqual(in_credits, credits.count(link), "credits " + link)

    def test_the_url_checker_can_fail(self):
        self.assertEqual([], unexpected_urls("a %s and %s and %s." % (ALLOWED_LINK, PORTAL_LINK, LOADER_LINK)))
        self.assertEqual(["https://github.com/Sharkmare/CasualtiesCharacters-loader-old"], unexpected_urls("x https://github.com/Sharkmare/CasualtiesCharacters-loader-old"))
        self.assertEqual(["https://skin.cat-bot.de/?skinid=52"], unexpected_urls("older: https://skin.cat-bot.de/?skinid=52"))
        self.assertEqual(["https://example.com/x"], unexpected_urls("see https://example.com/x, thanks"))

    def test_no_licence_or_reuse_wording_ships(self):
        with open(os.path.join(package.ROOT, "README.md"), encoding="utf-8") as handle:
            readme = handle.read()
        texts = [data.decode("utf-8") for name, data in self.entries.items() if name.lower().endswith(TEXT_SUFFIXES)] + [readme]
        for name in self.entries:
            self.assertEqual([], licence_wording(name), name)
        for text in texts:
            self.assertEqual([], licence_wording(text))

    def test_the_licence_wording_checker_can_fail(self):
        self.assertTrue(licence_wording("the portal states no reuse licence"))
        self.assertTrue(licence_wording("License: MIT"))
        self.assertTrue(licence_wording("Licence: MIT."))
        self.assertEqual([], licence_wording("Skin by paili16"))

    def test_the_link_checker_can_fail(self):
        self.assertEqual([], foreign_repository_text("see " + ALLOWED_LINK + " only"))
        self.assertTrue(foreign_repository_text("see https://github.com/someone/else"))
        self.assertTrue(foreign_repository_text("hosted on GitHub"))
        self.assertTrue(foreign_repository_text(ALLOWED_LINK + "-fork and https://github.com/x/y"))
        self.assertTrue(foreign_repository_text(ALLOWED_LINK + "-fork"))
        self.assertTrue(foreign_repository_text(ALLOWED_LINK + "/releases"))
        self.assertTrue(foreign_repository_text(TOGETHER_BASE_LINK + "/tree/main"))
        self.assertTrue(foreign_repository_text(TOGETHER_BASE_LINK))

    def test_the_link_line_is_omitted_when_the_constant_is_empty(self):
        original = package.TOGETHER_URL
        package.TOGETHER_URL = ""
        try:
            text = package.install_text("1.0.0")
        finally:
            package.TOGETHER_URL = original
        self.assertNotIn("built from the source", text)
        self.assertNotIn("casualties-together", text.lower())
        self.assertIn("installed by every player", text)
        self.assertNotIn("branch", text)
        self.assertNotIn("Download", text)

    def test_loader_link_author_and_licence_lines_are_omitted_until_set(self):
        self.assertEqual(LOADER_LINK, package.LOADER_URL)
        self.assertEqual(("", ""), (package.AUTHOR, package.LICENSE_NAME))
        text = package.install_text("1.0.0")
        for absent in ("Download:", "Made by", "Licence:"):
            self.assertNotIn(absent, text)
        original = package.LOADER_URL
        package.LOADER_URL = ""
        try:
            self.assertIn("The character loader, version", package.install_text("1.0.0"))
            self.assertNotIn("CasualtiesCharacters-loader", package.install_text("1.0.0"))
        finally:
            package.LOADER_URL = original
        package.AUTHOR, package.LICENSE_NAME = "Someone", "MIT"
        try:
            filled = package.install_text("1.0.0")
        finally:
            package.AUTHOR, package.LICENSE_NAME = "", ""
        self.assertIn("Made by Someone.", filled)
        self.assertIn("Licence: MIT.", filled)

    def test_build_is_reproducible(self):
        second = os.path.join(self.workdir.name, "again.zip")
        package.build(second, VERSION)
        self.assertEqual(package.file_md5(self.zip_path), package.file_md5(second))

    def test_rebuilding_over_a_zip_keeps_the_previous_one(self):
        target = os.path.join(self.workdir.name, "keep", "pkg.zip")
        package.build(target, "1.0.0")
        first_md5 = package.file_md5(target)
        package.build(target, "2.0.0")
        kept = os.path.join(os.path.dirname(target), "pkg.previous-%s.zip" % first_md5[:8])
        self.assertEqual(first_md5, package.file_md5(kept))
        self.assertNotEqual(first_md5, package.file_md5(target))


if __name__ == "__main__":
    unittest.main()
