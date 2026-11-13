BOING PLATFORM PIECES | BALLOON KINGDOM
======================================
PNG files are at the ZIP root. Use the existing filenames for the art
already wired up. The new gameplay sprites need to be assigned in the game.

Assemble a platform as left + zero or more full-width middle tiles + right.
Keep the three parts at the same y position. Local row 8 is the platform's
walk line. The standard spring shares that walk line. The compressed
spring uses the same canvas and bottom anchor with the top lowered.
Goal flag anchor is bottom center. The rubble sheet contains five separate
fragments on a 240 x 204 canvas.

Background wraps horizontally. Base bricks repeat in both axes.
For atlas-based imports, use sprite padding or edge extrusion to prevent
neighboring textures bleeding into a tile under linear filtering.

A) EXISTING PIECES
  cap-left.png     92 x 64   stone platform top, left end (sits on a brick base)
  cap-mid.png     302 x 64   stone platform top, middle (tiles sideways)
  cap-right.png    92 x 64   stone platform top, right end
  float-left.png  119 x 66   floating plank platform, left end
  float-mid.png   136 x 66   floating plank platform, middle (tiles sideways)
  float-right.png 119 x 66   floating plank platform, right end
  base-bricks.png 704 x 624  brick wall under the stone platforms. Must tile
                             seamlessly in BOTH directions. Lavender bricks,
                             running bond (each row offset by half a brick).
                             About 4 brick rows per 100 pixels feels right.
  deco-banner.png 190 x 220  hanging banner that decorates a brick base
  deco-vine.png   190 x 263  vine hanging off a platform corner
  bg-far.png     1704 x 828  far background (castle, hills). Must loop
                             left-to-right with no visible seam. Keep it
                             soft and hazy so platforms stand out in front.
  cloud-1/2/3.png  275x120, 172x100, 193x85   soft background clouds

B) NEW GAMEPLAY SPRITES
  Same height and walk line (row 8) as the caps, so they line up.
  brk-left.png / brk-mid.png / brk-right.png    92 / 136 / 92 x 64
       Breakable platform (crumbly, cracked, orange or wooden crate feel).
       Boing smashes through it. Middle tiles sideways.
  brk2-left.png / brk2-mid.png / brk2-right.png 92 / 136 / 92 x 64
       TOUGH breakable: same idea but armored (metal bands or bolts).
  brk2-cracked-left/mid/right.png               92 / 136 / 92 x 64
       The tough one after the first hit: armor gone, badly cracked.
  spring.png       128 x 80   bouncy spring pad (top surface at row 8).
  spring-squash.png 128 x 80  same spring pressed down.
  spikes-mid.png    64 x 48   a row of spikes, tiles sideways. Points up,
                              bottom edge flat. Danger red.
  goal-flag.png    120 x 200  the finish flag on its pole (pole bottom at
                              the bottom centre of the image).
  coin-world.png    64 x 64   the coin Boing collects in the level.
  piece-bits.png   240 x 204  five small rubble chunks (5 separate
                              bits on one transparent image) for when a
                              breakable smashes.

RULES
- Platform TOPS are the brightest, boldest thing on screen. Bases,
  background and clouds sit behind and are softer and less saturated,
  so a player never confuses scenery with something to land on.
- Keep the size of every piece exactly as listed so it drops straight in.
