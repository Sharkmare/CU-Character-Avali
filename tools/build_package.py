import argparse
import hashlib
import json
import os
import shutil
import sys
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PACK_DIRECTORY = os.path.join(ROOT, "pack")
CREDITS_SOURCE = os.path.join(ROOT, "CREDITS.md")
DEFAULT_OUTPUT_DIRECTORY = os.path.join(ROOT, "dist")
PRODUCT_NAME = "CasualtiesCharacters-Avali"
PACK_FOLDER = "BepInEx/plugins/" + PRODUCT_NAME
INSTALL_ENTRY = "INSTALL.txt"
CREDITS_ENTRY = PACK_FOLDER + "/CREDITS.md"
ZIP_TIMESTAMP = (2026, 1, 1, 0, 0, 0)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

BEPINEX_VERSION = "5.4.23.5"
LOADER_NAME = "character loader"
LOADER_MIN_VERSION = "0.2.0"
LOADER_URL = "https://github.com/Sharkmare/CasualtiesCharacters-loader"
TOGETHER_NAME = "Together co-op build with extra character support"
TOGETHER_BASE_VERSION = "5.4.1"
TOGETHER_MIN_COMMIT = "23d8cd2"
TOGETHER_URL = "https://github.com/Sharkmare/casualties-together"
AUTHOR = ""
LICENSE_NAME = ""

INSTALL_TEMPLATE = """{product} {version}

A character pack for the {loader}. It adds Avary, an Avali, as a playable character: small and
fast, quick to learn technical skills, but hungry, thirsty, fragile, poor at carrying and bad in
heat. The Avary skin by paili16 is included; source: https://skin.cat-bot.de/?skinid=200
See CREDITS.md.

Requirements
- Casualties: Unknown with BepInEx {bepinex}
- The {loader}{loader_from}, version {loader_min} or newer
{together_requirement}

Install
1. Close the game.
2. Unzip this file into the game folder (the one that contains CasualtiesUnknown.exe),
   so that BepInEx\\plugins\\{product}\\pack.json exists next to the loader's own folder.
3. Start the game. The pre-run screen shows a fourth character button.
To remove it, delete the folder BepInEx\\plugins\\{product}.
Do not load a save made as Avary without this pack.

Use
Pick Avary on the pre-run screen. Singleplayer works with the loader alone. For multiplayer every
player needs the loader, this pack and the Together build that supports extra characters. On any
other Together build Avary is not available in multiplayer and everything else stays vanilla. A
player without the pack sees the character as an Experiment.
The pack makes no network connections and adds no code of its own.

Known limitations
- Custom stats and perks are not shown on screen.
- In multiplayer Avary works only with the Together build that supports extra characters.
- Traits act on a player's own machine only; other players see the skin and the base body.
- A skin is only seen on machines that have the pack files.
{credits}"""


def loader_from():
    return " from " + LOADER_URL if LOADER_URL else ""


def together_requirement(singleplayer_note):
    if TOGETHER_URL:
        text = ("- For multiplayer: a %s, built from the source at %s\n"
                "  (main branch, commit %s or later; the repository's version number reads %s, so go by the commit;\n"
                "  see the Building section of its README), installed by every player") % (TOGETHER_NAME, TOGETHER_URL, TOGETHER_MIN_COMMIT, TOGETHER_BASE_VERSION)
    else:
        text = "- For multiplayer: a %s (based on version %s), installed by every player" % (TOGETHER_NAME, TOGETHER_BASE_VERSION)
    return text + "\n  " + singleplayer_note


def credits_text():
    lines = []
    if AUTHOR:
        lines.append("Made by " + AUTHOR + ".")
    if LICENSE_NAME:
        lines.append("Licence: " + LICENSE_NAME + ".")
    lines.append("The Avary skin credits are in CREDITS.md. Casualties: Unknown is made by its developers. BepInEx is by its authors.")
    return "\nCredits\n" + "\n".join(lines) + "\n"


def install_text(version):
    return INSTALL_TEMPLATE.format(product=PRODUCT_NAME, version=version, loader=LOADER_NAME, loader_min=LOADER_MIN_VERSION,
                                   loader_from=loader_from(), bepinex=BEPINEX_VERSION,
                                   together_requirement=together_requirement("Singleplayer works with the loader alone. With any other Together build Avary is not available\n  in multiplayer and everything else stays vanilla."), credits=credits_text())


def read_manifest(pack_directory=PACK_DIRECTORY):
    with open(os.path.join(pack_directory, "pack.json"), encoding="utf-8") as handle:
        return json.load(handle)


def read_version(pack_directory=PACK_DIRECTORY):
    return read_manifest(pack_directory)["version"]


def package_file_name(version):
    return "%s-%s.zip" % (PRODUCT_NAME, version)


def file_md5(path):
    with open(path, "rb") as handle:
        return hashlib.md5(handle.read()).hexdigest()


def keep_previous(output_path):
    if not os.path.isfile(output_path):
        return None
    stem, extension = os.path.splitext(output_path)
    kept = "%s.previous-%s%s" % (stem, file_md5(output_path)[:8], extension)
    if not os.path.exists(kept):
        shutil.copy2(output_path, kept)
    return kept


def pack_files(pack_directory=PACK_DIRECTORY):
    found = []
    for folder, _, names in os.walk(pack_directory):
        for name in names:
            path = os.path.join(folder, name)
            relative = os.path.relpath(path, pack_directory).replace(os.sep, "/")
            if relative.endswith(".png"):
                with open(path, "rb") as handle:
                    if handle.read(8) != PNG_SIGNATURE:
                        raise ValueError(relative + " is not a PNG")
            found.append((relative, path))
    return sorted(found)


def entries(version, pack_directory=PACK_DIRECTORY):
    content = {INSTALL_ENTRY: install_text(version).replace("\n", "\r\n").encode("utf-8")}
    with open(CREDITS_SOURCE, "rb") as handle:
        content[CREDITS_ENTRY] = handle.read()
    for relative, path in pack_files(pack_directory):
        with open(path, "rb") as handle:
            content[PACK_FOLDER + "/" + relative] = handle.read()
    return content


def build(output_path, version, pack_directory=PACK_DIRECTORY):
    content = entries(version, pack_directory)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    keep_previous(output_path)
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for entry in sorted(content):
            info = zipfile.ZipInfo(entry, ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content[entry])
    return output_path


def main(argv):
    parser = argparse.ArgumentParser(description="Build the CasualtiesCharacters-Avali release package.")
    parser.add_argument("--output-directory", default=DEFAULT_OUTPUT_DIRECTORY)
    arguments = parser.parse_args(argv)
    version = read_version()
    path = build(os.path.join(arguments.output_directory, package_file_name(version)), version)
    print(path)
    print("md5", file_md5(path))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
