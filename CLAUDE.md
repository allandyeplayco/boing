# Boing (working title): slam-bounce platformer prototype

## Who you're working with
- Allan is a game artist at Playco and new to Claude Code. Explain things plainly, skip jargon, and say what he should click or run.
- He tests on his phone. Every change has to work and feel right at portrait phone size.
- When he's unsure between two versions of a rule, add a toggle under **Feel** so he can compare them in play. Don't pick one for him.
- This prototype is a pitch for an original game. Work was asking employees for new game prototypes.

## Files
- `index.html`: the whole game in one file (HTML, CSS and JS, no build step). Open it in a browser to play. Boing's three sprites are embedded as data URIs (`SPRD`). When more poses arrive, move them to files under `art/`.
- `art/boing/`: cleaned, cropped full-res poses (`boing-fly.png`, `boing-slam.png`, `boing-dizzy.png`) and the character sheet.
- `docs/design-brief.md`: the design brief written for ChatGPT, which describes the mechanic and pieces in plain language. `docs/images/` holds the mechanic diagram and screenshots.
- `levels/`: Allan's early levels, as copied level codes.

## The mechanic (decided; don't change without asking)
- Boing bounces automatically and always moves sideways. One input: tap anywhere.
- **Tap = slam:** a short hang (`windup` 0.05 s), then a straight drop at `slamSpeed`, then a launch at `bounce × slamMult`.
- **Chaining (current rules, `turn:'chain'` + `chainReset:1`):** the 1st slam goes higher and keeps direction. The 2nd slam in a row is DOUBLE: higher still (`× comboStep`) and he **turns around**. After a double the chain resets, so the next slam is a 1st slam again. A normal bounce with no tap also resets the chain. TRIPLE and QUAD were tried and dropped as confusing; springs give extra height instead.
- **Late-tap grace:** a tap within `late` seconds after a normal landing still counts as a slam. With `lateFair:1` (default) the launch is trimmed so the peak matches an on-time slam; before, a late tap launched from partway up the bounce and went up to ~90 units higher.
- **Fast-tap turn (toggle `fastTurn`, off by default):** the turning slam only turns if tapped within `fastWindow` after the previous slam landed. A blue ring around Boing shows the window.
- **Breakable (`brk`):** breaks on the 1st slam. With `brkThrough:1` the slam **ends** at the smash: Boing keeps falling fast but not slamming, and does a **normal** bounce on whatever is below, even another breakable. A normal bounce never damages a breakable.
- **Tough breakable (`brk2`):** the 1st slam cracks it and removes the armor; slam number `brkHits` (default 2) breaks it.
- **Spring:** multiplies any bounce by `springMult`.
- **Spikes:** kill. Falling 1600 units below the last landing also kills. With `restartOnDeath:1`, death restarts the level after a 0.5 s dizzy pose.
- **Goal flag:** big celebration (hit-stop, slow-mo, rays, confetti, FLAG! banner, stats, best time saved per level). The next tap moves to the next level.
- The ball only collides with platform **tops**, falling downward. Boing passes up through platforms from below.

## Physics and units
- Fixed 120 Hz step (`step(1/120)`), so a run is deterministic given the same tap times. The solver depends on this.
- y grows **down**. 40 units = 1 m in the HUD. Ball hitbox radius `R=18`. Platform thickness `PH=18`.
- Defaults (`DEF`): gravity 2600, bounce 1000, speed 270, slamSpeed 2600, slamMult 1.6, comboStep 1.15, springMult 1.7, late 0.1, zoom 1, look-ahead 120.
- Peak heights: normal ≈ 190 units (about 5 m), 1st slam ≈ 490 (about 12 m), double ≈ 650 (about 16 m), slam on a spring ≈ 1420.
- The camera shows about 640 units across at zoom 1 (`baseScale = min(W,H)/640`).

## Code map (in `index.html`)
- Settings: `FEEL` (slider and toggle definitions; `'seg'` type = button group, with options in `SEGS`) and `DEF`. Settings save under the key `sbl_feel`.
- Core loop: `tap()`, `step()`, `land()`, `doSlamBounce()`, `hitBrk()`, `nextCombo()`, `turnsAt()`, `die()`, `startPlay()`.
- Win: `celebrate()`, `winStep()`, `showBanner()`.
- Drawing: `render()`, `drawObj()`, `drawBall()`, `drawBoing()`. Boing is drawn with his body's bottom on the hitbox's bottom, scaled by `boingSize` (default 1.5×; visual only, the hitbox never changes). He flips with direction. The dizzy pose shows during death.
- Levels: the 20-level campaign is `CAMPAIGN` (each level has a `teach` list). `pack` holds 20 slots (saved under `sbl_pack`, tagged `camp:CAMP_VER`); `starter(i)` returns a fresh copy of `CAMPAIGN[i]`. A pack from before the campaign is backed up to `sbl_pack_old`. Bump `CAMP_VER` to push a new campaign over saved packs. Endless random world in `cell()`. Best times are saved under `sbl_best_<hash>`.
- Level bot (`// ---------- level bot ----------`): `botSearch()` runs the real `step()` with `SIM=true` (no sound, buzz or saved times) and searches tap timings landing by landing. `botCheck()` solves a level, measures each tap's timing window (`botTolerance()`), and searches again with each `teach` move banned to find shortcuts. The **Bot** button opens the sheet with **Watch this level** (plays the bot's taps through `BOT.watch` in the real loop) and **Check all levels**. Headless: `node tools/check.mjs [levels.json]` prints the same table for the campaign or a file of levels.
- Editor: drag-and-drop palette, move, resize handle, duplicate, delete, snap 20, level code import and export, copy previous level, reset to starter.
- `cloudBoot()` and `window.claude`: saving to Allan's Claude account. This only works when the page runs as a claude.ai artifact. Anywhere else it does nothing and saving falls back to localStorage. It's safe to leave in or remove.

## Level format
`{"name":"…","spawn":{"x":0,"y":-60,"dir":1},"objs":[{"id":1,"type":"plat","x":-200,"y":0,"w":400}, …]}`
- Types: `plat`, `brk`, `brk2`, `spring` (w 64), `spike`, `coin`, `goal`.
- Bar pieces are placed by their top-left corner (`x`, `y` = top surface, `w` = width). Coins and the goal are placed by their center.
- A spring's top surface is at `y`, and its base sits 20 units lower. To seat a spring on a platform, use spring `y` = platform `y` − 20.

## Next up (agreed plan)
1. **Done (first pass):** 20 levels with a difficulty curve, in `CAMPAIGN`. **Was:** 20 levels with a difficulty curve. Introduce one move at a time: bounce, then slam for height, double to turn, breakables, smash-through, springs, spikes, tough breakables, fast-tap turn (only if enabled), then combinations. Each new move gets a level or two to itself before levels mix moves.
2. **Done (first pass):** solver bot, see the code map. **Was:** solver bot. Run the game headless (Playwright and Chromium work; pause the rAF loop and drive `step()` directly) and search for tap timings that reach the flag, deciding at each bounce whether and when to tap. For each level, record:
   - a winning tap sequence,
   - its timing tolerance (how much each tap can shift and still win) as a difficulty number,
   - whether the level can be won *without* the move it teaches (a shortcut means the level needs fixing).

   Add a **Watch solution** button per level and a **Check all levels** action to rerun after any Feel change. Winnable doesn't mean fun, so Allan still playtests.
3. **Sprites.** Allan has fal.ai in Claude Code. The plan is a few consistent key poses plus motion in code (squash, stretch, tilt, spin). The poses needed: rise (stretch), apex, fall, slam drop (stretched down, determined face), impact squash, DOUBLE spin or turn, dizzy, win. Keep effects (bursts, smoke) **out** of the pose images and draw them in the game, because the current slam pose has them baked in and they show during the fall. Align every pose to the same body circle; the original anchors were found with a distance transform on the alpha mask.
4. **Art direction rule for platforms:** every landable top shares one strong, consistent cap style. Structures and scenery sit behind it, darker and less saturated, so they never look solid. Keep the space under platforms clear, because players fall through there. Hanging supports (chains from above) work better than pillars. A mix of floating and attached platforms is fine as long as that rule holds.
5. **Deploy to playco.dev** once the 20 levels are in. Playco uses `play-co/web-cli` (an npm package on GitHub Packages, `@play-co/web-cli`). Run `playco-web deploy <folder> --name slam-bounce` → `https://slam-bounce.playco.dev`. The folder needs `index.html` at its root. The tool is for experiments, not production, and the URL is public to anyone with the link. Ask Rishav or Chris Wu how to install it (it needs GitHub auth for npm.pkg.github.com).
