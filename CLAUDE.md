# Boing (working title): slam-bounce platformer prototype

## Who you're working with
- Allan is a game artist at Playco and new to Claude Code. Explain things plainly, skip jargon, and say what he should click or run.
- He tests on his phone. Every change has to work and feel right at portrait phone size. On a computer the game shows inside a 390×844 portrait phone frame (Feel toggle `phoneFrame`, on by default; CSS under `html.phone`, only at 600px wide and up), so he can judge it there too. Keep it on.
- When he's unsure between two versions of a rule, add a toggle under **Feel** so he can compare them in play. Don't pick one for him.
- This prototype is a pitch for an original game. Work was asking employees for new game prototypes.

## Files
- `index.html`: the whole game in one file (HTML, CSS and JS, no build step). Open it in a browser to play. Boing's three sprites are embedded as data URIs (`SPRD`). When more poses arrive, move them to files under `art/`.
- `art/boing/`: the original poses (`boing-fly.png`, `boing-slam.png`, `boing-dizzy.png`) and the character sheet.
- `art/boing/poses/<pose>.png`: the game's pose pictures (rise, apex, fall, land, slam, dead, win), first made with fal (nano-banana-pro edit + birefnet) and meant for Allan to touch up. `python3 tools/pack_sprites.py --embed` aligns them (equal silhouette area, centred on the body; `land` sits on its feet) into `art/boing/game/` and embeds them in `index.html`.
- `art/boing/spine/`: Allan's Spine export (`boing.json`, `boing.atlas`, `boing.png`; JSON with packed atlas, facing right, root at the body's bottom). Animations: `air` (scrubbed by vertical speed: frame 0 = launching up, middle = apex, end = falling), `land`, `slam`, `dead`, `win`, and `summersault` (plays once when he turns around on a DOUBLE, instead of `land`). The game loads it with the Spine canvas runtime from jsDelivr (`SPINE_VER` in `index.html` must match his editor version). Character `Boing (Spine)` falls back to the pictures when no export is there. Over `file://` the browser blocks loading it, so test through a local web server or the artifact.
- `docs/design-brief.md`: the design brief written for ChatGPT, which describes the mechanic and pieces in plain language. `docs/images/` holds the mechanic diagram and screenshots.
- `levels/`: Allan's early levels, as copied level codes.

## The mechanic (decided; don't change without asking)
- Boing bounces automatically and always moves sideways. One input: tap anywhere.
- **Tap = slam:** a short hang (`windup` 0.05 s), then a straight drop at `slamSpeed`, then a launch at `bounce × slamMult`.
- **Chaining (current rules, `turn:'chain'` + `chainReset:1`):** the 1st slam goes higher and keeps direction. The 2nd slam in a row is DOUBLE: higher still (`× comboStep`) and he **turns around**. After a double the chain resets, so the next slam is a 1st slam again. A normal bounce with no tap also resets the chain. TRIPLE and QUAD were tried and dropped as confusing; springs give extra height instead.
- **Late-tap grace:** a tap within `late` seconds after a normal landing still counts as a slam. With `lateFair:1` (default) the launch is trimmed so the peak matches an on-time slam; before, a late tap launched from partway up the bounce and went up to ~90 units higher.
- **Fast-tap turn (toggle `fastTurn`, on by default):** the turning slam only turns if tapped within `fastWindow` after the previous slam landed. A blue ring around Boing shows the window.
- **Breakable (`brk`):** breaks on the 1st slam. With `brkThrough:1` the slam **ends** at the smash: Boing keeps falling fast but not slamming, and does a **normal** bounce on whatever is below, even another breakable. A normal bounce never damages a breakable.
- **Tough breakable (`brk2`):** the 1st slam cracks it and removes the armor; slam number `brkHits` (default 2) breaks it.
- **Spring:** multiplies any bounce by `springMult`.
- **Spikes:** kill. Falling 1600 units below the last landing also kills. With `restartOnDeath:1`, death restarts the level after a 0.5 s dizzy pose.
- **Goal flag:** big celebration (hit-stop, slow-mo, rays, confetti, FLAG! banner, stats, best time saved per level). The next tap moves to the next level.
- The ball only collides with platform **tops**, falling downward. Boing passes up through platforms from below.

## Physics and units
- Fixed 120 Hz step (`step(1/120)`), so a run is deterministic given the same tap times. The solver depends on this.
- y grows **down**. 40 units = 1 m in the HUD. Ball hitbox radius `R=18`. Platform thickness `PH=18`.
- Defaults (`DEF`, Allan's tuned feel from 2026-11-11): gravity 2600, bounce 1000, speed 270, slamSpeed 2600, windup 0.04, slamMult 1.29, comboStep 1.06, springMult 1.65, late 0.08, fastTurn on (fastWindow 0.28), zoom 1, look-ahead 120.
- Peak heights (defaults): normal ≈ 190 units (about 5 m), 1st slam ≈ 320 (about 8 m), double ≈ 360 (about 9 m), spring alone ≈ 520, slam on a spring ≈ 870.
- The camera shows about 640 units across at zoom 1 (`baseScale = min(W,H)/640`).

## Code map (in `index.html`)
- Settings: `FEEL` (slider and toggle definitions; `'seg'` type = button group, with options in `SEGS`) and `DEF`. Settings save under the key `sbl_feel`.
- Core loop: `tap()`, `step()`, `land()`, `doSlamBounce()`, `hitBrk()`, `nextCombo()`, `turnsAt()`, `die()`, `startPlay()`.
- Win: `celebrate()`, `winStep()`, `showBanner()`. The popup (`#win .w-panel`, styled after Allan's purple/cream ChatGPT design `art/ui/src/level-clear-concept-2.png` (the older navy one is `level-clear-concept.png`); baked pictures `art/ui/title.png` ("Level clear!"), `crown.png`, shiny `star.png`, `star-empty.png`, `coin.png` cut by `python3 tools/cut_ui.py`; NEW BEST / FIRST CLEAR is plain colourful text, no pill, per Allan) shows Level clear!, 1–3 stars, slams, coins found / total, time. Stars: `levelPar()` = fewest slams the bot finds (computed once per layout + physics Feel at level start, saved as `sbl_par_<hash>`); `starsFor()`: ≤ par = 3, ≤ par + `starStep(par)` (max(2, ½ par)) = 2, else 1. Best stars saved as `sbl_best_<hash>_stars`.
- Level start: `introStart()`/`introTick()` (Feel `intro`: `fly` = camera starts on the flag and glides to Boing, `zoom` = whole level shown then zooms in, `off`). Runs only on a level's first try, not after deaths or for the bot; a tap skips it. `drawGoalArrow()` pins a flag badge to the screen edge pointing at an off-screen flag (Feel `goalArrow`).
- Drawing: `render()`, `drawObj()`, `drawBall()`, `drawBoing()`. Boing is drawn with his body's bottom on the hitbox's bottom, scaled by `boingSize` (default 1.5×; visual only, the hitbox never changes). He flips with direction. `pickPose()` chooses rise/apex/fall/land/slam/dead/win from his motion, and `drawBoing()` fades into the new pose over `poseBlend` s, with `tilt` and `squashAmt` (Feel sliders) on top.
- World art (painted, `// ---------- world art (painted) ----------`): Feel `art` default `painted`. Pieces cut from Allan's ChatGPT concept (`art/world/src/concept-1.png`) by `python3 tools/cut_world.py` into `art/world/*.png` (needs opencv-python-headless): 3-slice caps `cap-*` (anchored) and `float-*` (plank platform), brick tile `base-bricks` (drawn crisp by `python3 tools/make_bricks.py`, running bond, 4 px per unit; `base-mid` is the old blurry cut, unused), decorations `deco-banner`/`deco-vine`, `bg-far` (mirrored so it loops), `cloud-1..3`. Drawn at `ART_K` 0.55 units per pixel; walk line = pixel row 8 of each cap. Bases layer like the greybox. Breakables still use the code drawing. Pictures load from `art/world/`, so the artifact publish must include them via `files`.
- World art (greybox, `// ---------- world art (greybox) ----------`): Feel `art` (`greybox` = world art, `plain` = old flat look), `anchor` (which platforms get a base on Auto: `wide` = 300+ units, `all`, `none`) and `bgDepth` (parallax). `drawWorldBg()` draws sky, clouds, far hills and mid towers at slower scroll speeds. `drawStructures()` draws what's under each bar piece, behind everything: `lookOf()` returns `base` (stone column going down and fading), `float` (small underside) or `none` (spring or spike sitting on a platform). Bases are layered Mario-style: lower platforms' bases in front, higher ones behind and hazier. Breakables always float. Allan dropped hanging chains (2026-11-13). Per-piece override: the editor's **Look** button (Auto / Ground / Floating), saved as `look` in the level code. `drawCap()` is the one cream cap style on every landable top. The art brief for the real art is the Claude Doc "Boing world art brief" (https://claude.ai/artifact/UvbRCNtPxKCcputYxKsy7j).
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
4. **Art direction rule for platforms:** every landable top shares one strong, consistent cap style. Structures and scenery sit behind it, darker and less saturated, so they never look solid. Keep the space under platforms clear, because players fall through there. Allan's call (2026-11-13): some platforms stand on bases that go down to the world below, layered like old Mario (lower bases in front, higher bases behind); breakables and some platforms just float. No hanging chains.
5. **Deploy to playco.dev** once the 20 levels are in. Playco uses `play-co/web-cli` (an npm package on GitHub Packages, `@play-co/web-cli`). Run `playco-web deploy <folder> --name slam-bounce` → `https://slam-bounce.playco.dev`. The folder needs `index.html` at its root. The tool is for experiments, not production, and the URL is public to anyone with the link. Ask Rishav or Chris Wu how to install it (it needs GitHub auth for npm.pkg.github.com).
