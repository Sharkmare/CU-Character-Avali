# Development

This repository is a data-only character pack for the CasualtiesCharacters loader (repository `CU Characters`, next to this one). Traits come from the loader's trait library, so there is no code and no build step for the pack itself.

## Layout

```
pack/pack.json                    pack id, version, minimum loader version
pack/characters/avali_avary.json  the character
pack/skins/avary/Body/*.png       the skin (34 PNGs, portal id 200)
CREDITS.md                        the skin credit chain, shipped in the pack folder
tools/build_package.py            builds dist/CasualtiesCharacters-Avali-<version>.zip
tools/extract_skin.py             extracts only Body/*.png from a portal zip, checking PNG signatures
```

The pack id (`avali`) namespaces everything: the character is `avali/avary`, its skin is looked up in this pack's own `skins/` folder, and its id is derived from that key (the loader documents the rule). The file asks for id 3; if another pack asked first, the loader moves one of them and logs it.

## Test (offline, no game launch)

```
python -I -m unittest discover -s tests/package
python -I -m unittest discover -s tests/pack
python -I -m unittest discover -s tests/commitcheck
```

- `package`: exact entries, hashes after unzipping, PNG signatures, banned wording in every shipped name and text, the loader requirement matching `pack.json`, previous zips kept.
- `pack`: runs the loader's `PackCheck` tool over `pack/` (loader repository found next to this one, or set `CU_CHARACTERS_REPOSITORY`). Fails on any parser warning, a missing skin part or a rejected manifest.
- `commitcheck`: the commit message rules.

## Package

```
python tools/build_package.py
```

The zip goes to `dist/`. An existing zip is copied to `*.previous-<md5>.zip` first. The constants at the top of `tools/build_package.py` (`LOADER_MIN_VERSION`, `LOADER_URL`, `TOGETHER_MIN_VERSION`, `TOGETHER_URL`, `AUTHOR`, `LICENSE_NAME`) feed `INSTALL.txt`; empty links, author and licence lines are omitted.

## Updating the skin

Download the portal zip by hand, then `python tools/extract_skin.py <zip> pack/skins/avary/Body`. Keep `CREDITS.md` in step.

## Commits

`git config core.hooksPath .githooks` turns on the message check: one subject line of at most 72 characters, no ticket keys, none of the internal words.
