I'm a game artist at a mobile game studio. We've been asked to pitch original game prototypes, and I have a working prototype of a one-tap mobile platformer I want to develop into a full design. Please help me design it. I've attached images of the prototype (described at the bottom). The mechanic below is already built, tuned and fun in my hands, so treat it as fixed and design around it rather than redesigning it.

## The core mechanic (built and playable)

- The character is a ball that bounces automatically and constantly moves sideways (left or right). The player never steers.
- The only input is a tap anywhere on the screen.
- Tap = SLAM. The ball cancels its current arc, drops straight down fast, hits the platform below and launches much higher than a normal bounce.
- Slams chain in pairs:
  - 1st slam: big bounce (about 2.5× normal height). The ball keeps going the same direction.
  - 2nd slam in a row (tapping again during the 1st slam's bounce): "DOUBLE!" Even bigger bounce (about 3.4× normal height), and the ball TURNS AROUND.
  - After a double, the chain resets, so the next slam is a 1st slam again.
  - If you let one normal bounce happen without tapping, the chain also resets.
- So the player's only decisions are when to slam (timing and position) and whether to follow up with a second slam to reverse direction. Direction changes always cost a double slam.
- There is a small grace window: a tap just after landing a normal bounce still counts as a slam.
- Optional rule (toggle, currently off): the second slam only turns you around if the tap comes quickly (within about 0.35 s of the previous slam landing). A late second tap gives the height but no turn.

## Pieces that exist in the prototype

- Platform: solid. Bounce off it.
- Breakable (orange): shatters on the first slam. The ball does not bounce back. It keeps falling at speed to whatever is below and does a normal bounce there. If there's nothing below, it falls and dies. A normal bounce does not break it.
- Tough breakable (orange with dark armored outline): the first slam cracks it (armor comes off), the second slam breaks it.
- Spring: multiplies any bounce (about 1.7×). A slam on a spring is the biggest launch in the game.
- Spikes: touching them kills you.
- Coins: optional collectibles.
- Goal flag: touch it to win the level. There's a big celebration (slow-mo, confetti, fanfare, time/coins/slams stats, best-time tracking).
- Dying, including falling too far, restarts the level instantly.

## Feel numbers (current tuning, for reference)

- World units: 40 units = 1 meter on screen. Ball diameter 36 units. Platform thickness 18.
- Normal bounce peak: about 190 units (about 5 m).
- 1st slam bounce peak: about 490 units (about 12 m).
- Double slam bounce peak: about 650 units (about 16 m).
- Spring + slam peak: about 1400 units.
- Sideways speed: 270 units/s. While slamming the ball drops straight down (no sideways drift).
- The camera follows the ball and the world scrolls in all directions (up, down, left, right). Portrait phone screen.

## What I'd like from you

1. A level progression for 20 levels that teaches one idea at a time: bounce, then slam for height, double to turn around, breakables, smash-through drops, springs, spikes, tough breakables, and finally combinations. For each level give a name, the one idea it teaches or tests, a short description of the layout, and how a player wins. Early levels should be nearly impossible to fail. Later levels should demand precise timing and planning.
2. Level-design patterns that only make sense with this mechanic. For example: a ledge reachable only with a slam, a corridor where you must double to turn back at a wall of spikes, smashing down through a stack of breakables one layer per tap, or a spring you must reach going the right direction.
3. Ideas for 3–5 new pieces or hazards that would add depth without adding new inputs. Keep it one tap.
4. Theme and art direction ideas. I'm an artist, so the current shapes are placeholders. Who is the character, what's the world, and why do they bounce?
5. A light meta loop suitable for a mobile prototype pitch (stars per level, unlocks, etc.), kept small.
6. 5–10 name ideas.

Optional: if you sketch level layouts, you can write them in the prototype's level format so I can load them directly. Coordinates are in world units, y grows DOWNWARD, platforms are placed by top-left corner, and coins and the goal are placed by their center. Example:
{"spawn":{"x":0,"y":-60,"dir":1},"objs":[{"id":1,"type":"plat","x":-200,"y":0,"w":400},{"id":2,"type":"brk","x":300,"y":-200,"w":160},{"id":3,"type":"coin","x":380,"y":-300},{"id":4,"type":"goal","x":520,"y":-440}]}
Types: plat, brk (breakable), brk2 (tough breakable), spring (w 64), spike, coin, goal. dir is 1 for right, -1 for left.

## Attached images

- 00-mechanic-diagram: height over time recorded from the real physics, showing normal bounces, a slam, a double that turns around, and the chain resetting.
- 01-auto-bounce: normal automatic bouncing (the yellow ball).
- 02-slam-drop: the ball mid-slam, dropping straight down.
- 03-slam-bounce: the 1st slam landing and launching higher.
- 04-double-turn: a DOUBLE! slam, where the ball turns around (↺).
- 05-breakable-smash: a slam smashing through a breakable and falling to the platform below.
- 06-flag: reaching the goal flag.
- 07-editor: the built-in level editor, with drag-and-drop pieces.
