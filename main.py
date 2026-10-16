"""
OPERATION DARK ISLAND: LAST STAND
A single-player survival + adventure + mission shooter prototype.

Install:
    python -m pip install -r requirements.txt

Run:
    python main.py

Controls:
    WASD / Arrow keys : Move
    Mouse             : Aim
    Left click        : Shoot
    E                 : Pick up nearby supplies / interact
    H                 : Use a medkit
    P                 : Pause
    F5                : Save game
    F9                : Load game
    ESC               : Quit
"""

import json
import math
import random
import sys
from pathlib import Path

import pygame

pygame.init()

# ---------------------------- Configuration ----------------------------
SCREEN_W, SCREEN_H = 1000, 700
FPS = 60
WORLD_W, WORLD_H = 2200, 1700
TITLE = "Operation Dark Island: Last Stand"
SAVE_PATH = Path(__file__).with_name("savegame.json")

OCEAN = (28, 91, 125)
SAND = (194, 177, 118)
GRASS = (66, 117, 70)
GRASS_DARK = (52, 96, 61)
WHITE = (245, 245, 235)
INK = (20, 25, 28)
RED = (210, 65, 58)
YELLOW = (244, 207, 89)
CYAN = (88, 213, 225)
GREEN = (100, 255, 170)
BLUE = (72, 128, 220)
PURPLE = (155, 106, 194)

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()
FONT = pygame.font.Font(None, 27)
SMALL = pygame.font.Font(None, 21)
BIG = pygame.font.Font(None, 54)
HUGE = pygame.font.Font(None, 76)


def clamp(value, low, high):
    return max(low, min(high, value))


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def draw_text(surface, text, font, color, pos, center=False):
    image = font.render(str(text), True, color)
    rect = image.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surface.blit(image, rect)
    return rect


class Player:
    def __init__(self, x=300, y=300):
        self.x, self.y = float(x), float(y)
        self.radius = 15
        self.health = 100
        self.hunger = 100
        self.thirst = 100
        self.ammo = 45
        self.medkits = 2
        self.speed = 235
        self.cooldown = 0
        self.invulnerable = 0

    @property
    def pos(self):
        return (self.x, self.y)

    def update(self, dt, keys, world):
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        length = math.hypot(dx, dy)
        if length:
            dx, dy = dx / length, dy / length
        self.x += dx * self.speed * dt
        self.y += dy * self.speed * dt
        self.x = clamp(self.x, 45, WORLD_W - 45)
        self.y = clamp(self.y, 45, WORLD_H - 45)
        self.cooldown = max(0, self.cooldown - dt)
        self.invulnerable = max(0, self.invulnerable - dt)
        # Survival meters slowly drain. Running the clock too long has consequences.
        self.hunger = max(0, self.hunger - 0.42 * dt)
        self.thirst = max(0, self.thirst - 0.72 * dt)
        if self.hunger <= 0 or self.thirst <= 0:
            self.health = max(0, self.health - 3.0 * dt)

    def draw(self, surface, camera):
        sx, sy = int(self.x - camera[0]), int(self.y - camera[1])
        mouse_x, mouse_y = pygame.mouse.get_pos()
        angle = math.atan2(mouse_y - sy, mouse_x - sx)
        tip = (sx + math.cos(angle) * 24, sy + math.sin(angle) * 24)
        if self.invulnerable <= 0 or int(self.invulnerable * 12) % 2 == 0:
            pygame.draw.circle(surface, (27, 35, 42), (sx, sy), self.radius + 3)
            pygame.draw.circle(surface, CYAN, (sx, sy), self.radius)
            pygame.draw.line(surface, WHITE, (sx, sy), tip, 5)
            pygame.draw.circle(surface, WHITE, (sx, sy), 4)


class Enemy:
    def __init__(self, x, y, kind="raider"):
        self.x, self.y = float(x), float(y)
        self.kind = kind
        self.radius = 16 if kind == "commander" else 13
        self.health = 65 if kind == "commander" else 40
        self.speed = 80 if kind == "commander" else random.randint(65, 88)
        self.attack_cooldown = random.uniform(0.3, 1.1)
        self.alive = True

    @property
    def pos(self):
        return (self.x, self.y)

    def update(self, dt, player):
        if not self.alive:
            return
        d = distance(self.pos, player.pos)
        if d < 420 and d > self.radius + player.radius + 5:
            dx = (player.x - self.x) / d
            dy = (player.y - self.y) / d
            self.x += dx * self.speed * dt
            self.y += dy * self.speed * dt
        self.attack_cooldown -= dt
        if d < 38 and self.attack_cooldown <= 0 and player.invulnerable <= 0:
            player.health = max(0, player.health - (13 if self.kind == "commander" else 8))
            player.invulnerable = 0.55
            self.attack_cooldown = 0.9

    def draw(self, surface, camera):
        if not self.alive:
            return
        sx, sy = int(self.x - camera[0]), int(self.y - camera[1])
        color = PURPLE if self.kind == "commander" else RED
        pygame.draw.circle(surface, (30, 25, 25), (sx, sy), self.radius + 3)
        pygame.draw.circle(surface, color, (sx, sy), self.radius)
        pygame.draw.circle(surface, YELLOW, (sx - 4, sy - 3), 3)
        pygame.draw.circle(surface, YELLOW, (sx + 4, sy - 3), 3)
        bar_w = 34
        pygame.draw.rect(surface, (35, 35, 35), (sx - bar_w // 2, sy - 24, bar_w, 5))
        pygame.draw.rect(surface, (80, 220, 100),
                         (sx - bar_w // 2, sy - 24, int(bar_w * max(0, self.health) / (65 if self.kind == "commander" else 40)), 5))


class Loot:
    COLORS = {
        "ammo": YELLOW,
        "food": (120, 220, 100),
        "water": CYAN,
        "medkit": (245, 245, 245),
        "intel": (255, 165, 60),
    }
    LABELS = {"ammo": "Ammo", "food": "Food", "water": "Water", "medkit": "Medkit", "intel": "Intel"}

    def __init__(self, x, y, kind):
        self.x, self.y, self.kind = x, y, kind
        self.taken = False

    @property
    def pos(self):
        return (self.x, self.y)

    def draw(self, surface, camera):
        if self.taken:
            return
        sx, sy = int(self.x - camera[0]), int(self.y - camera[1])
        color = self.COLORS[self.kind]
        pygame.draw.rect(surface, (25, 31, 28), (sx - 11, sy - 11, 22, 22), border_radius=4)
        pygame.draw.rect(surface, color, (sx - 8, sy - 8, 16, 16), border_radius=3)
        if self.kind == "intel":
            pygame.draw.line(surface, INK, (sx - 4, sy - 3), (sx + 4, sy - 3), 2)
            pygame.draw.line(surface, INK, (sx - 4, sy + 1), (sx + 4, sy + 1), 2)


class Game:
    def __init__(self):
        self.player = Player(240, 280)
        self.enemies = [
            Enemy(650, 300), Enemy(730, 360), Enemy(1030, 540),
            Enemy(1450, 400), Enemy(1540, 460), Enemy(1720, 1120),
            Enemy(1770, 1180), Enemy(1100, 1320), Enemy(1850, 700, "commander")
        ]
        self.loot = [
            Loot(360, 240, "ammo"), Loot(440, 500, "food"), Loot(560, 650, "water"),
            Loot(830, 300, "intel"), Loot(1170, 500, "medkit"), Loot(1450, 650, "intel"),
            Loot(1650, 900, "food"), Loot(1880, 1080, "water"), Loot(1300, 1250, "intel"),
            Loot(960, 1450, "ammo"), Loot(500, 1200, "medkit"), Loot(1800, 400, "ammo")
        ]
        self.rescue_pos = (1040, 1050)
        self.extraction_pos = (2000, 1500)
        self.rescued = False
        self.score = 0
        self.paused = False
        self.game_over = False
        self.won = False
        self.message = "Mission 1: Collect 3 intel files (orange crates)."
        self.message_timer = 5
        self.total_time = 0

        # Fixed scenery, generated once for repeatable landmarks.
        rng = random.Random(27)
        self.trees = [(rng.randint(90, WORLD_W-90), rng.randint(90, WORLD_H-90), rng.randint(13, 25))
                      for _ in range(135)]
        self.buildings = [
            (610, 220, 145, 105, "OUTPOST"), (980, 450, 155, 120, "VILLAGE"),
            (1390, 350, 170, 130, "MILITARY BASE"), (1660, 1040, 160, 120, "BUNKER"),
            (880, 1280, 130, 100, "RADIO TOWER")
        ]

    def say(self, text, seconds=3.5):
        self.message = text
        self.message_timer = seconds

    def nearby_loot(self):
        candidates = [item for item in self.loot if not item.taken and distance(item.pos, self.player.pos) < 48]
        return min(candidates, key=lambda item: distance(item.pos, self.player.pos)) if candidates else None

    def interact(self):
        item = self.nearby_loot()
        if item:
            item.taken = True
            if item.kind == "ammo":
                self.player.ammo += 20
                self.say("Collected ammunition (+20).")
            elif item.kind == "food":
                self.player.hunger = min(100, self.player.hunger + 45)
                self.say("Food collected. Hunger restored.")
            elif item.kind == "water":
                self.player.thirst = min(100, self.player.thirst + 50)
                self.say("Clean water collected. Thirst restored.")
            elif item.kind == "medkit":
                self.player.medkits += 1
                self.say("Medkit collected (+1). Press H to use.")
            elif item.kind == "intel":
                self.score += 100
                count = sum(1 for x in self.loot if x.kind == "intel" and x.taken)
                if count >= 3:
                    self.say("Intel secured! Next: rescue the survivor (blue marker).", 5)
                else:
                    self.say(f"Intel secured ({count}/3). Find the remaining files.", 3)
        elif not self.rescued and distance(self.player.pos, self.rescue_pos) < 65:
            self.rescued = True
            self.score += 250
            self.say("Survivor rescued! Reach the extraction zone (green marker).", 5)
        elif distance(self.player.pos, self.extraction_pos) < 70:
            if self.rescued and sum(1 for x in self.loot if x.kind == "intel" and x.taken) >= 3:
                self.won = True
                self.score += 500
            else:
                self.say("Extraction locked: collect 3 intel files and rescue the survivor.", 4)
        else:
            self.say("Nothing nearby to interact with.", 1.5)

    def shoot(self):
        p = self.player
        if p.cooldown > 0 or self.paused or self.game_over or self.won:
            return
        if p.ammo <= 0:
            self.say("Out of ammunition! Search supply crates.", 2)
            p.cooldown = 0.25
            return
        mx, my = pygame.mouse.get_pos()
        cam = self.camera()
        target = (mx + cam[0], my + cam[1])
        dx, dy = target[0] - p.x, target[1] - p.y
        length = math.hypot(dx, dy) or 1
        dx, dy = dx / length, dy / length
        # Bullets are short-lived line segments in world coordinates.
        self.bullets.append([p.x + dx * 20, p.y + dy * 20, dx * 620, dy * 620, 1.2])
        p.ammo -= 1
        p.cooldown = 0.18

    def camera(self):
        return (clamp(self.player.x - SCREEN_W / 2, 0, WORLD_W - SCREEN_W),
                clamp(self.player.y - SCREEN_H / 2, 0, WORLD_H - SCREEN_H))

    def save(self):
        data = {
            "player": {k: getattr(self.player, k) for k in ("x", "y", "health", "hunger", "thirst", "ammo", "medkits")},
            "loot_taken": [i for i, item in enumerate(self.loot) if item.taken],
            "enemies": [{"x": e.x, "y": e.y, "health": e.health, "alive": e.alive, "kind": e.kind} for e in self.enemies],
            "rescued": self.rescued, "score": self.score
        }
        SAVE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self.say("Game saved (F5).", 2)

    def load(self):
        if not SAVE_PATH.exists():
            self.say("No save file found yet. Press F5 to save.", 3)
            return
        try:
            data = json.loads(SAVE_PATH.read_text(encoding="utf-8"))
            for key, value in data["player"].items():
                setattr(self.player, key, value)
            taken = set(data["loot_taken"])
            for i, item in enumerate(self.loot):
                item.taken = i in taken
            for i, saved in enumerate(data["enemies"]):
                if i < len(self.enemies):
                    self.enemies[i].x = saved["x"]
                    self.enemies[i].y = saved["y"]
                    self.enemies[i].health = saved["health"]
                    self.enemies[i].alive = saved["alive"]
            self.rescued = data["rescued"]
            self.score = data["score"]
            self.game_over = self.player.health <= 0
            self.say("Save loaded.", 2)
        except (ValueError, KeyError, OSError) as exc:
            self.say(f"Could not load save: {exc}", 3)

    def update(self, dt, keys):
        if self.paused or self.game_over or self.won:
            return
        self.total_time += dt
        self.player.update(dt, keys, self)
        for enemy in self.enemies:
            enemy.update(dt, self.player)
        if not hasattr(self, "bullets"):
            self.bullets = []
        for bullet in self.bullets[:]:
            bullet[0] += bullet[2] * dt
            bullet[1] += bullet[3] * dt
            bullet[4] -= dt
            if bullet[4] <= 0 or not (0 <= bullet[0] <= WORLD_W and 0 <= bullet[1] <= WORLD_H):
                self.bullets.remove(bullet)
                continue
            for enemy in self.enemies:
                if enemy.alive and distance((bullet[0], bullet[1]), enemy.pos) < enemy.radius + 5:
                    enemy.health -= 35
                    if enemy.health <= 0:
                        enemy.alive = False
                        self.score += 50 if enemy.kind != "commander" else 200
                        if enemy.kind == "commander":
                            self.say("Enemy commander defeated! Keep moving.", 3)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break
        self.player.cooldown = max(0, self.player.cooldown - dt)
        self.message_timer = max(0, self.message_timer - dt)
        if self.player.health <= 0:
            self.game_over = True

    def draw_world(self):
        camx, camy = self.camera()
        screen.fill(OCEAN)
        # Main island landmass with a sandy coastline.
        island_rect = pygame.Rect(int(35-camx), int(35-camy), WORLD_W-70, WORLD_H-70)
        pygame.draw.rect(screen, SAND, island_rect, border_radius=100)
        inner = island_rect.inflate(-34, -34)
        pygame.draw.rect(screen, GRASS, inner, border_radius=88)

        # Light paths create navigable routes across the island.
        path_points = [(180, 330), (610, 300), (900, 480), (1390, 410), (1610, 720), (1670, 1080), (1980, 1480)]
        pygame.draw.lines(screen, (155, 145, 100), False,
                          [(int(x-camx), int(y-camy)) for x, y in path_points], 25)
        pygame.draw.lines(screen, (184, 171, 123), False,
                          [(int(x-camx), int(y-camy)) for x, y in path_points], 18)

        # Scenery
        for x, y, r in self.trees:
            sx, sy = int(x-camx), int(y-camy)
            if -40 <= sx <= SCREEN_W+40 and -40 <= sy <= SCREEN_H+40:
                pygame.draw.circle(screen, GRASS_DARK, (sx+4, sy+5), r+2)
                pygame.draw.circle(screen, (35, 79, 47), (sx, sy), r)
                pygame.draw.circle(screen, (76, 133, 73), (sx-4, sy-5), max(5, r-7))

        for x, y, w, h, label in self.buildings:
            rect = pygame.Rect(int(x-camx), int(y-camy), w, h)
            pygame.draw.rect(screen, (48, 53, 57), rect.inflate(8, 8), border_radius=5)
            pygame.draw.rect(screen, (128, 126, 111), rect, border_radius=4)
            pygame.draw.rect(screen, (69, 74, 72), rect, 3, border_radius=4)
            pygame.draw.rect(screen, (52, 60, 60), (rect.centerx-13, rect.centery-9, 26, 38))
            draw_text(screen, label, SMALL, WHITE, (rect.centerx, rect.top-14), center=True)

        # Mission markers
        if not self.rescued:
            x, y = self.rescue_pos
            sx, sy = int(x-camx), int(y-camy)
            pygame.draw.circle(screen, BLUE, (sx, sy), 24, 4)
            pygame.draw.circle(screen, WHITE, (sx, sy), 8)
            draw_text(screen, "RESCUE", SMALL, WHITE, (sx, sy-36), center=True)
        x, y = self.extraction_pos
        sx, sy = int(x-camx), int(y-camy)
        color = (70, 230, 125) if self.rescued else (160, 160, 160)
        pygame.draw.circle(screen, color, (sx, sy), 28, 4)
        pygame.draw.circle(screen, color, (sx, sy), 7)
        draw_text(screen, "EXTRACT", SMALL, WHITE, (sx, sy-40), center=True)

        for item in self.loot:
            item.draw(screen, (camx, camy))
        for enemy in self.enemies:
            enemy.draw(screen, (camx, camy))
        for bullet in getattr(self, "bullets", []):
            sx, sy = int(bullet[0]-camx), int(bullet[1]-camy)
            pygame.draw.circle(screen, YELLOW, (sx, sy), 4)
            pygame.draw.circle(screen, WHITE, (sx, sy), 2)
        self.player.draw(screen, (camx, camy))

    def draw_hud(self):
        panel = pygame.Surface((SCREEN_W, 92), pygame.SRCALPHA)
        panel.fill((10, 17, 20, 205))
        screen.blit(panel, (0, 0))
        draw_text(screen, "OPERATION DARK ISLAND", FONT, WHITE, (16, 10))
        draw_text(screen, f"Score {self.score}", FONT, YELLOW, (SCREEN_W-145, 10))
        self.draw_bar("HEALTH", self.player.health, RED, 16, 43, 180)
        self.draw_bar("HUNGER", self.player.hunger, (117, 208, 95), 225, 43, 150)
        self.draw_bar("THIRST", self.player.thirst, CYAN, 395, 43, 150)
        draw_text(screen, f"Ammo: {self.player.ammo}", SMALL, WHITE, (575, 44))
        draw_text(screen, f"Medkits: {self.player.medkits} (H)", SMALL, WHITE, (700, 44))
        draw_text(screen, "WASD move â€¢ Mouse aim â€¢ Click shoot â€¢ E interact â€¢ F5 save â€¢ F9 load â€¢ P pause",
                  SMALL, (220, 226, 220), (16, SCREEN_H-25))
        if self.message_timer > 0:
            box = pygame.Rect(170, 104, SCREEN_W-340, 38)
            pygame.draw.rect(screen, (14, 22, 25), box, border_radius=8)
            pygame.draw.rect(screen, (210, 210, 190), box, 1, border_radius=8)
            draw_text(screen, self.message, SMALL, WHITE, (SCREEN_W//2, 123), center=True)

        # Minimap
        mini_w, mini_h = 150, 115
        mini_x, mini_y = SCREEN_W-mini_w-15, SCREEN_H-mini_h-40
        pygame.draw.rect(screen, (15, 35, 35), (mini_x, mini_y, mini_w, mini_h), border_radius=6)
        pygame.draw.rect(screen, (190, 180, 135), (mini_x+4, mini_y+4, mini_w-8, mini_h-8), border_radius=10)
        def mp(pos):
            return (mini_x+7+int(pos[0]/WORLD_W*(mini_w-14)),
                    mini_y+7+int(pos[1]/WORLD_H*(mini_h-14)))
        for enemy in self.enemies:
            if enemy.alive:
                pygame.draw.circle(screen, RED, mp(enemy.pos), 2)
        pygame.draw.circle(screen, BLUE if not self.rescued else GREEN, mp(self.rescue_pos), 3)
        pygame.draw.circle(screen, YELLOW, mp(self.player.pos), 4)
        pygame.draw.circle(screen, GREEN, mp(self.extraction_pos), 3)

    def draw_bar(self, label, value, color, x, y, width):
        draw_text(screen, label, SMALL, WHITE, (x, y-17))
        pygame.draw.rect(screen, (55, 60, 62), (x, y, width, 12), border_radius=4)
        pygame.draw.rect(screen, color, (x, y, int(width*clamp(value, 0, 100)/100), 12), border_radius=4)

    def draw_overlay(self, title, subtitle, footer):
        shade = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        shade.fill((4, 9, 13, 205))
        screen.blit(shade, (0, 0))
        draw_text(screen, title, HUGE, WHITE, (SCREEN_W//2, SCREEN_H//2-75), center=True)
        draw_text(screen, subtitle, FONT, YELLOW, (SCREEN_W//2, SCREEN_H//2), center=True)
        draw_text(screen, footer, FONT, CYAN, (SCREEN_W//2, SCREEN_H//2+58), center=True)


def main():
    game = Game()
    game.bullets = []
    running = True
    while running:
        dt = min(clock.tick(FPS)/1000.0, 0.035)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_p and not game.game_over and not game.won:
                    game.paused = not game.paused
                elif event.key == pygame.K_e and not game.paused:
                    game.interact()
                elif event.key == pygame.K_h and not game.paused:
                    if game.player.medkits > 0 and game.player.health < 100:
                        game.player.medkits -= 1
                        game.player.health = min(100, game.player.health + 40)
                        game.say("Medkit used (+40 health).")
                    else:
                        game.say("No medkits available, or health is already full.", 2)
                elif event.key == pygame.K_F5:
                    game.save()
                elif event.key == pygame.K_F9:
                    game.load()
                elif event.key == pygame.K_RETURN and (game.game_over or game.won):
                    game = Game()
                    game.bullets = []
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                game.shoot()

        keys = pygame.key.get_pressed()
        game.update(dt, keys)
        game.draw_world()
        game.draw_hud()
        if game.paused and not game.game_over and not game.won:
            game.draw_overlay("PAUSED", "Take a breath, survivor.", "Press P to continue â€¢ ESC to quit")
        elif game.game_over:
            game.draw_overlay("YOU WERE LOST", f"Final score: {game.score}", "Press ENTER to restart â€¢ ESC to quit")
        elif game.won:
            game.draw_overlay("MISSION COMPLETE", f"Extraction successful â€¢ Score: {game.score}", "Press ENTER to play again â€¢ ESC to quit")
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

