# Live checklist (not run)

Everything here needs a running game and has not been executed. Install the loader and this pack first. Log: `BepInEx/LogOutput.log`.

1. Startup log shows `character 3 = avali/avary (base experiment, pack version 1.0.0)`, a `character table fingerprint` line and `skin avali/avary: matched 33 of 33`. A line `skin ... not found in its pack` means the skin folder is misplaced.
2. With a second pack installed that also asks for id 3, the log shows one of them at 3 and the other at a derived id, the same on every restart and on the other machine.
3. The pre-run screen has the extra button; selecting it shows the name Avary, the family text with the quote, the quirks line and `[STR] 5 [RES] 6 [INT] 11`.
4. In a run the body is the Experiment shape with the Avali art. Parts that stay Experiment-coloured have sprite names missing from the skin (turn on Debug in the loader's cfg and compare the dumped names).
5. Traits against Experiment: freezes later, hungrier and thirstier, faster walk, lower carry limit, pain and bleeding build faster, explosions hurt hearing more, no sweating.
6. Molt: play about 33 minutes, sleep, wake; with Debug on, the log shows the fresh plumage perk turning on and, ten minutes later, off.
7. Save and load: comes back as Avary. Remove the pack and the loader falls back to the base character without crashing.
8. Multiplayer with the Together build that supports extra characters (every machine has the loader and this pack): the fingerprints in the logs match; each player sees the others as Avary; a machine without the pack sees an Experiment; traits act on the owner's machine only. On any other Together build Avary must not appear in multiplayer: the player spawns as an Experiment and the game is vanilla.
9. Respawn with the Together rule RespawnKeepSkills off: skills are 5 / 6 / 11 again after respawn.
10. Size mod: a size command still scales the Avali and keeps its traits.
