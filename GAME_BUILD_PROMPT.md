# Excellent Game Development Prompt — Operation Dark Island: Last Stand

Act as a senior game designer and Python game developer. Build a playable, polished, modular single-player survival-adventure shooter prototype named **Operation Dark Island: Last Stand**.

## High-level concept
The player is a special-operations survivor stranded on a hostile tropical island after a helicopter crash. The player must scavenge supplies, survive enemy encounters, collect intelligence, rescue a captive survivor, and reach an extraction point. The mood should feel tense, adventurous, tactical, and rewarding. The broad inspiration is survival-island games and battle-royale shooters, but do not copy proprietary characters, maps, names, artwork, sounds, or other protected content.

## Scope and non-negotiable constraints
- Build a single-player, offline-first prototype now.
- Do NOT implement open-world multiplayer in this version.
- Multiplayer and a larger connected world are future expansion ideas only.
- Choose a feasible Python implementation. Use Pygame for a reliable 2D prototype, or explicitly explain before changing engines.
- The current target is Windows PC.
- Use original code and placeholder/drawn graphics when assets are unavailable.
- Do not claim this is a full 3D game or comparable in production quality to a commercial shooter.
- Prioritize a complete playable loop over an oversized feature list.

## Core gameplay requirements
1. Player movement with WASD and arrow keys; smooth normalized diagonal movement.
2. Mouse aiming and click-to-shoot combat.
3. Health, damage feedback, ammunition, reload/resupply behavior, and healing items.
4. Enemies that can patrol or idle, detect the player within a range, pursue, attack at close range, take damage, and die.
5. At least one stronger elite enemy/commander.
6. Survival systems for hunger and thirst that drain over time and damage the player when depleted.
7. Loot pickups: ammunition, food, water, medkits, and intelligence documents.
8. Interaction key for collecting loot, rescuing an NPC, and activating extraction.
9. Mission objectives with clear UI and state progression:
   - collect three intelligence files;
   - rescue one survivor;
   - reach the extraction zone and activate it.
10. Mission success and failure screens, score, restart, and pause.
11. Scrolling island map with ocean/coast, sand, grass, jungle trees, paths, buildings, enemy camps, rescue point, extraction zone, and minimap.
12. Save and load core progress locally.
13. On-screen control hints, HUD bars, ammo/medkit counters, objective text, and feedback messages.
14. Keep gameplay functional without internet access after dependencies are installed.

## Technical requirements
- Python 3.10+ recommended.
- Pygame 2.5+.
- Provide a clean project folder with `main.py`, `requirements.txt`, and `README.md`.
- Organize code into readable classes or modules for player, enemies, loot, missions, and game state when reasonable.
- Use delta time for movement and timers.
- Avoid crashes on window close, missing save files, and invalid save data.
- Use collision checks and clamp the player to the map boundaries.
- Avoid relying on external assets that are not included.
- Include clear installation and run instructions for Windows/VS Code.
- Include controls, mission instructions, limitations, and future work in the README.
- Keep the game runnable from a fresh folder with `python -m pip install -r requirements.txt` followed by `python main.py`.

## Quality expectations
- Use consistent naming and comments.
- Provide readable UI, a cohesive color palette, and meaningful visual feedback.
- Keep game state logic separate from rendering as much as practical.
- Test the main game loop, movement, shooting, enemy defeat, pickups, mission progression, save/load, restart, and quit behavior.
- Be honest about any feature that is a prototype or not yet implemented.

## Future-proofing (do not build these now)
Structure code so future development can introduce:
- More mission types and story chapters.
- Additional island regions and map transitions.
- Better art, animation, audio, settings, and controller support.
- Vehicles, crafting, base upgrades, and more enemy types.
- Optional multiplayer later, which will require a separate networking design, authoritative state, synchronization, security, and testing. Do not add fake multiplayer buttons or imply networking already exists.

## Deliverables
1. Complete runnable source code.
2. `requirements.txt`.
3. A clear `README.md`.
4. A concise list of controls and how to complete the first mission.
5. A list of known limitations and realistic next development steps.
6. A ZIP package that can be extracted and run locally.

Before finishing, verify the file structure, ensure imports are correct, check syntax, and ensure the README's commands match the actual project. If a requested feature cannot be fully implemented, state that clearly instead of pretending it works.
