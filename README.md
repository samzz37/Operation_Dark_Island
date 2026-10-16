# Operation Dark Island: Last Stand

A single-player survival, adventure, and mission-based shooter prototype made with Python and Pygame.

## Current prototype includes
- A scrolling island map with coastline, forest, paths, buildings, an outpost, village, military base, bunker, and radio tower.
- Third-person-style top-down presentation (2D prototype; not a 3D game).
- Keyboard movement, mouse aiming, shooting, ammunition, health, and enemy AI.
- Survival meters for hunger and thirst.
- Collectable food, water, ammo, medkits, and intelligence files.
- Mission chain: collect 3 intel files, rescue a survivor, and reach extraction.
- Enemy patrol/chase behavior, including an elite commander.
- Score, minimap, pause, restart, save, and load.

## Requirements
- Python 3.10 or newer recommended
- Pygame 2.5 or newer

## Run on Windows
1. Install Python from the official Python website if it is not installed.
2. Extract this ZIP file.
3. Open the extracted folder in VS Code.
4. Open Terminal → New Terminal.
5. Run:

   ```bash
   python -m pip install -r requirements.txt
   python main.py
   ```

If `python` is not recognized, try `py -m pip install -r requirements.txt` and `py main.py`.

## Controls
- WASD or arrow keys: move
- Mouse: aim
- Left mouse button: shoot
- E: collect nearby loot / interact with survivor or extraction
- H: use medkit
- P: pause/resume
- F5: save
- F9: load
- Enter: restart after winning or losing
- Esc: quit

## Mission instructions
1. Search for orange intel crates and press E near them. Collect 3.
2. Find the blue RESCUE marker and press E nearby.
3. Reach the green EXTRACT marker and press E to finish the mission.
4. Stay alive. Collect food and water before your hunger or thirst reaches zero.

## Scope and future plan
This is an offline single-player prototype, not an open-world multiplayer game and not a 3D commercial-scale shooter. It is deliberately scoped so it can be improved in stages.

Potential future features:
- More missions, story dialogue, enemy types, and boss encounters.
- A larger world with separated regions and loading boundaries.
- Better animations, sound effects, music, original art, and settings.
- Vehicles, crafting, base upgrades, and save-slot management.
- Controller support and accessibility options.
- Multiplayer only as a later project phase, requiring networking, server authority, synchronization, anti-cheat considerations, testing, and significant redesign. Multiplayer is not implemented now.

## Known prototype limitations
- Visuals are drawn from simple shapes; no external art assets are required.
- Enemy behavior is intentionally basic.
- This is a 2D top-down prototype, not a realistic 3D game.
- Save/load stores core player, enemy, loot, rescue, and score progress.
