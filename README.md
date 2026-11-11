# CasualtiesCharacters-Avali

A character pack for the character loader, for Casualties: Unknown. It adds Avary, an Avali, as a playable character.

## Avary

A small feathered cold-world character. Fast and quick to learn technical skills, but hungry, thirsty, fragile, poor at carrying and bad in heat. The pack is data only: a character file and a skin, no code.

| | Avary | Experiment |
|---|---|---|
| Strength / Resistance / Intelligence | 5 / 6 / 11 | 9 / 8 / 7 |
| Skill gain (STR / RES / INT) | 0.8 / 0.8 / 1.25 | 1 / 1 / 1 |
| Insulation | 1.6 times | 1 times |
| Hunger / thirst drain | 1.3 / 1.15 times | 1 times |
| Thirst while hot | 1.8 times above 37.5 degrees | 1 times |
| Walking force / stamina recovery | 1.1 / 1.15 times | 1 times |
| Carry limit | 0.75 times | 1 times |
| Pain / bleeding build-up | 1.25 / 1.2 times | 1 times |
| Hearing damage | 1.5 times | 1 times |
| Sweating | none | yes |

Avary also has a molt stat that fills slowly; after a full molt and a night's sleep, fresh plumage adds warmth for ten minutes.

## Requirements

- Casualties: Unknown with BepInEx 5.4.23.5
- The character loader from https://github.com/Sharkmare/CasualtiesCharacters-loader, version 0.2.0 or newer
- For multiplayer: a Together co-op build with extra character support, built from the source at https://github.com/Sharkmare/casualties-together/tree/characters (the characters branch is the one with the extra character support; its README has a Building section), with the loader and this pack on every player's game. No prebuilt download is offered.
- Singleplayer works with the loader alone. On any other Together build Avary is not available in multiplayer and everything else stays vanilla.

## Install

1. Close the game.
2. Unzip the release into the game folder (the one that contains `CasualtiesUnknown.exe`), so that `BepInEx/plugins/CasualtiesCharacters-Avali/pack.json` exists next to the loader's own folder.
3. Start the game. The pre-run screen shows a fourth character button.

To remove it, delete the folder `BepInEx/plugins/CasualtiesCharacters-Avali`. Do not load a save made as Avary without the pack.

## Known limitations

- Custom stats and perks are not shown on screen.
- In multiplayer Avary works only with a Together co-op build that has extra character support.
- Traits act on a player's own machine only; other players see the skin and the base body.
- A skin is only seen on machines that have the pack files.

## Credits

Skin by paili16, source https://skin.cat-bot.de/?skinid=200. See `CREDITS.md`.

## Development

Build, test and design notes are in `docs/dev/`.
