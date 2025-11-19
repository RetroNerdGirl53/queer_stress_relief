#!/usr/bin/python3

"""
Stress Relief Target Game - Python/Pygame Version

Install requirements:
pip install pygame

Run with:
python game.py

Controls:
- SPACE: Change weapon
- Click & Drag in launch area (bottom of screen) to aim and fire
- ESC: Quit game
"""
#window size is SCREEN_WIDTH and SCREEN_HEIGHT
#playable area is window size minus ui elements
#Target hitbox is TARGET_SIZE
#Ammo hitbox is PROJECTILE_SIZE

import pygame
import random
import math
import time
import os

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Colors
BLACK = (26, 26, 46)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
PINK = (255, 100, 255)
BROWN = (139, 69, 19)

# Game settings
TARGET_SIZE = 80
PROJECTILE_SIZE = 40
POWERUP_SIZE = 100


class Weapon:
    """Represents a weapon with its properties"""
    def __init__(self, name, projectile_type, speed, projectile_size, fire_sound_path, hit_sound_path, is_homing=False):
        self.name = name
        self.projectile_type = projectile_type
        self.speed = speed
        self.projectile_size = projectile_size
        self.fire_sound_path = fire_sound_path
        self.hit_sound_path = hit_sound_path
        self.is_homing = is_homing


class Projectile:
    """Represents a fired projectile."""
    def __init__(self, x, y, vx, vy, is_homing=False, ammo_index=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.is_homing = is_homing
        self.ammo_index = ammo_index
        self.active = True
        self.trail = []  # For visual trail effect


class Target:
    """The moving target to hit"""
    def __init__(self, x, y, vx, vy, size):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.is_straight = True  # Pride Parade seeks straight targets!


class PowerUp:
    """Leather Daddy power-up that moves across screen"""
    def __init__(self, x, y, vx, size):
        self.x = x
        self.y = y
        self.vx = vx
        self.size = size
        self.active = True


class Enemy:
    """Represents an enemy with unique attributes"""
    def __init__(self, name, image_filename, size, speed_multiplier, evasion_pattern, description, font_path, music_track):
        self.name = name
        self.image_filename = image_filename
        self.image = None  # Loaded in load_enemies
        self.size = size
        self.speed_multiplier = speed_multiplier
        self.evasion_pattern = evasion_pattern
        self.description = description
        self.font_path = font_path
        self.music_track = music_track


class Game:
    """Main game class."""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Stress Relief Target Game")
        pygame.mixer.init()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Initialize weapons with all 12 types
        self.weapons = [
            Weapon("Slingshot", "Vegetables", 15, 30, "fire_slingshot.ogg", "hit_slingshot.ogg"),
            Weapon("Bottle Rockets", "Rockets", 20, 25, "fire_rocket.ogg", "hit_rocket.ogg"),
            Weapon("Catapult", "Boulders", 12, 50, "fire_catapult.ogg", "hit_catapult.ogg"),
            Weapon("Tomato BB Gun", "Tomatoes", 25, 20, "fire_bbgun.ogg", "hit_bbgun.ogg"),
            Weapon("Poison Bow", "Poison Arrows", 18, 35, "fire_bow.ogg", "hit_bow.ogg"),
            Weapon("Marshmallow Crossbow", "Flaming Marshmallows", 16, 25, "fire_crossbow.ogg", "hit_crossbow.ogg"),
            Weapon("Darts", "Darts", 22, 15, "fire_dart.ogg", "hit_dart.ogg"),
            Weapon("Throwing Stars", "Shuriken", 24, 25, "fire_star.ogg", "hit_star.ogg"),
            Weapon("Potato Cannon", "Potatoes", 17, 40, "fire_cannon.ogg", "hit_cannon.ogg"),
            Weapon("Frog Cannon", "Gay Frogs", 17, 45, "fire_frog.ogg", "hit_frog.ogg"),
            Weapon("Trans Missile", "Guided Missile", 10, 55, "fire_missile.ogg", "hit_missile.ogg", is_homing=True),
            Weapon("Pride Parade", "Rainbow Seeker", 14, 60, "fire_pride.ogg", "hit_pride.ogg", is_homing=True)
        ]

        # Load weapon images (or create placeholders if not found)
        self.weapon_images = {}
        self.load_weapon_images()

        self.ammo_images = {}
        self.load_ammo_images()

        self.sounds = {}
        self.load_sounds()

        self.current_weapon_index = 0
        self.projectiles = []
        self.target = None
        self.powerup = None
        self.score = 0

        # Power-up state
        self.powerup_active = False
        self.powerup_end_time = 0
        self.next_powerup_time = time.time() + random.uniform(15, 30)

        # Touch/mouse state
        self.is_touching = False
        self.touch_x = SCREEN_WIDTH // 2  # Start centered
        self.touch_y = 0
        self.weapon_x = SCREEN_WIDTH // 2  # Weapon follows mouse X

        self.state = 'enemy_selection'
        self.enemies = []
        self.selected_enemy = None
        self.load_enemies()

        self.reset_target()
        self.running = True

    def load_weapon_images(self):
        """Load or create placeholder weapon images"""
        weapon_files = [
            'weapon_slingshot.png', 'weapon_rocket.png', 'weapon_catapult.png',
            'weapon_bbgun.png', 'weapon_bow.png', 'weapon_crossbow.png',
            'weapon_darts.png', 'weapon_star.png', 'weapon_cannon.png',
            'weapon_cannon.png',  # Reuse for frog cannon
            'weapon_missile.png', 'weapon_pride.png'
        ]

        for i, filename in enumerate(weapon_files):
            image_loaded = False

            # Try multiple paths
            possible_paths = [
                os.path.join('images', 'weapons', filename),
                os.path.join('weapons', filename),
                filename
            ]

            for path in possible_paths:
                try:
                    img = pygame.image.load(path)
                    img = pygame.transform.scale(img, (120, 120))  # Larger weapon display
                    self.weapon_images[i] = img
                    image_loaded = True
                    print(f"✓ Loaded {filename} from {path}")
                    break
                except:
                    continue

            if not image_loaded:
                # Create placeholder if image not found
                print(f"✗ Could not load {filename}, using placeholder")
                surface = pygame.Surface((120, 120), pygame.SRCALPHA)
                weapon = self.weapons[i]

                # Draw colored circle
                color_map = {
                    'Slingshot': (139, 69, 19),
                    'Bottle Rockets': (255, 68, 68),
                    'Catapult': (102, 102, 102),
                    'Tomato BB Gun': (51, 51, 51),
                    'Poison Bow': (0, 170, 0),
                    'Marshmallow Crossbow': (139, 69, 19),
                    'Darts': (255, 102, 0),
                    'Throwing Stars': (255, 215, 0),
                    'Potato Cannon': (205, 133, 63),
                    'Frog Cannon': (0, 255, 0),
                    'Trans Missile': (85, 205, 252),
                    'Pride Parade': (255, 105, 180)
                }

                color = color_map.get(weapon.name, WHITE)
                pygame.draw.circle(surface, color, (60, 60), 50)
                pygame.draw.circle(surface, BLACK, (60, 60), 50, 4)

                # Add simple icon/text
                font = pygame.font.Font(None, 30)
                text = font.render(weapon.name[:3].upper(), True, WHITE)
                text_rect = text.get_rect(center=(60, 60))
                surface.blit(text, text_rect)

                self.weapon_images[i] = surface

    def load_ammo_images(self):
        """Load or create placeholder ammo images"""
        ammo_files = [
            'ammo_vegetable.png', 'ammo_rocket.png', 'ammo_boulder.png',
            'ammo_tomato.png', 'ammo_poison_arrow.png', 'ammo_marshmallow.png',
            'ammo_dart.png', 'ammo_star.png', 'ammo_potato.png',
            'ammo_frog.png', 'ammo_trans_missile.png', 'ammo_pride.png'
        ]

        for i, filename in enumerate(ammo_files):
            image_loaded = False
            projectile_size = self.weapons[i].projectile_size

            # Try multiple paths
            possible_paths = [
                os.path.join('images', 'ammo', filename),
                os.path.join('ammo', filename),
                filename
            ]

            for path in possible_paths:
                try:
                    img = pygame.image.load(path)
                    img = pygame.transform.scale(img, (projectile_size, projectile_size))
                    self.ammo_images[i] = img
                    image_loaded = True
                    print(f"✓ Loaded {filename} from {path}")
                    break
                except:
                    continue

            if not image_loaded:
                # Create placeholder if image not found
                print(f"✗ Could not load {filename}, using placeholder")
                surface = pygame.Surface((projectile_size, projectile_size), pygame.SRCALPHA)

                # Use yellow circle as placeholder
                pygame.draw.circle(surface, YELLOW, (projectile_size//2, projectile_size//2), projectile_size//2 - 2)
                pygame.draw.circle(surface, BLACK, (projectile_size//2, projectile_size//2), projectile_size//2 - 2, 2)

                self.ammo_images[i] = surface

    def load_enemies(self):
        """Load enemies from a definition list and their images from files"""
        enemy_definitions = [
            {"name": "Standard", "img": "enemy_standard.png", "size": 80, "speed": 1.0, "pattern": "random", "desc": "A classic bullseye.", "font": "font_standard.ttf", "music": "music_standard.ogg"},
            {"name": "Quickster", "img": "enemy_quick.png", "size": 40, "speed": 1.8, "pattern": "bounce", "desc": "Small, fast, and erratic.", "font": "font_quick.ttf", "music": "music_quick.ogg"},
            {"name": "Tank", "img": "enemy_tank.png", "size": 120, "speed": 0.6, "pattern": "horizontal", "desc": "Large and slow-moving.", "font": "font_tank.ttf", "music": "music_tank.ogg"},
            {"name": "Dodger", "img": "enemy_dodger.png", "size": 60, "speed": 1.2, "pattern": "evade", "desc": "Tries to avoid projectiles.", "font": "font_dodger.ttf", "music": "music_dodger.ogg"},
            {"name": "Ghost", "img": "enemy_ghost.png", "size": 70, "speed": 1.1, "pattern": "random", "desc": "Fades in and out.", "font": "font_ghost.ttf", "music": "music_ghost.ogg"},
            {"name": "Spinner", "img": "enemy_spinner.png", "size": 50, "speed": 1.5, "pattern": "bounce", "desc": "Spins wildly as it moves.", "font": "font_spinner.ttf", "music": "music_spinner.ogg"},
            {"name": "Cloner", "img": "enemy_cloner.png", "size": 90, "speed": 0.8, "pattern": "horizontal", "desc": "Splits into smaller clones.", "font": "font_cloner.ttf", "music": "music_cloner.ogg"},
            {"name": "Shadow", "img": "enemy_shadow.png", "size": 60, "speed": 1.3, "pattern": "evade", "desc": "Moves in the shadows.", "font": "font_shadow.ttf", "music": "music_shadow.ogg"}
        ]

        for definition in enemy_definitions:
            enemy = Enemy(definition["name"], definition["img"], definition["size"], definition["speed"], definition["pattern"], definition["desc"], definition["font"], definition["music"])

            try:
                path = os.path.join('images', 'enemies', enemy.image_filename)
                img = pygame.image.load(path)
                enemy.image = pygame.transform.scale(img, (enemy.size, enemy.size))
                print(f"✓ Loaded enemy image: {enemy.image_filename}")
            except pygame.error:
                print(f"✗ Could not load enemy image: {enemy.image_filename}. Creating placeholder.")
                surface = pygame.Surface((enemy.size, enemy.size), pygame.SRCALPHA)
                # Simple placeholder: a colored circle
                color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
                pygame.draw.circle(surface, color, (enemy.size // 2, enemy.size // 2), enemy.size // 2)
                enemy.image = surface

            self.enemies.append(enemy)

    def load_sounds(self):
        """Load all sound effects"""
        self.sounds = {}
        for weapon in self.weapons:
            try:
                self.sounds[weapon.fire_sound_path] = pygame.mixer.Sound(os.path.join('audio', 'sfx', weapon.fire_sound_path))
            except pygame.error:
                print(f"✗ Could not load sound: {weapon.fire_sound_path}")
            try:
                self.sounds[weapon.hit_sound_path] = pygame.mixer.Sound(os.path.join('audio', 'sfx', weapon.hit_sound_path))
            except pygame.error:
                print(f"✗ Could not load sound: {weapon.hit_sound_path}")

        try:
            self.sounds["select"] = pygame.mixer.Sound(os.path.join('audio', 'sfx', 'select.ogg'))
            self.sounds["powerup"] = pygame.mixer.Sound(os.path.join('audio', 'sfx', 'powerup.ogg'))
        except pygame.error:
            print("✗ Could not load UI or power-up sounds.")

    def reset_target(self):
        """Reset target to a new random position with random velocity"""
        if not self.selected_enemy:
            return  # Don't create a target if no enemy is selected

        size = self.selected_enemy.size
        speed = self.selected_enemy.speed_multiplier
        pattern = self.selected_enemy.evasion_pattern

        vx = random.uniform(-4, 4) * speed
        vy = random.uniform(-4, 4) * speed

        if pattern == "horizontal":
            vy = 0
        elif pattern == "vertical":
            vx = 0

        self.target = Target(
            x=random.uniform(size, SCREEN_WIDTH - size),
            y=random.uniform(size, SCREEN_HEIGHT / 2 - size),
            vx=vx,
            vy=vy,
            size=size
        )

    def spawn_powerup(self):
        """Spawn Leather Daddy power-up from a random edge of screen"""
        side = random.randint(0, 3)

        if side == 0:  # Left
            x, y = -POWERUP_SIZE, random.uniform(0, SCREEN_HEIGHT)
        elif side == 1:  # Right
            x, y = SCREEN_WIDTH + POWERUP_SIZE, random.uniform(0, SCREEN_HEIGHT)
        elif side == 2:  # Top
            x, y = random.uniform(0, SCREEN_WIDTH), -POWERUP_SIZE
        else:  # Bottom
            x, y = random.uniform(0, SCREEN_WIDTH), SCREEN_HEIGHT + POWERUP_SIZE

        # Calculate velocity to move toward center
        vx = (SCREEN_WIDTH / 2 - x) / 100

        self.powerup = PowerUp(x, y, vx, POWERUP_SIZE)

    def update(self):
        """Update all game state each frame"""
        current_time = time.time()

        # Check if power-up effect expired
        if self.powerup_active and current_time > self.powerup_end_time:
            self.powerup_active = False

        # Spawn new power-up if it's time
        if self.powerup is None and current_time > self.next_powerup_time:
            self.spawn_powerup()

        # Update power-up position
        if self.powerup:
            self.powerup.x += self.powerup.vx

            # Remove if off screen
            if (self.powerup.x < -POWERUP_SIZE * 2 or
                self.powerup.x > SCREEN_WIDTH + POWERUP_SIZE * 2):
                self.powerup = None
                self.next_powerup_time = current_time + random.uniform(15, 30)

        # Update target position
        if self.target:
            # Evasion behavior
            if self.selected_enemy and self.selected_enemy.evasion_pattern == "evade":
                for proj in self.projectiles:
                    dist = math.hypot(self.target.x - proj.x, self.target.y - proj.y)
                    if dist < 150:  # Evasion radius
                        # Move away from the projectile
                        self.target.x += (self.target.x - proj.x) * 0.02
                        self.target.y += (self.target.y - proj.y) * 0.02

            self.target.x += self.target.vx
            self.target.y += self.target.vy

            # Bounce off walls
            if self.target.x - self.target.size < 0 or self.target.x + self.target.size > SCREEN_WIDTH:
                self.target.vx = -self.target.vx
                self.target.x = max(self.target.size, min(SCREEN_WIDTH - self.target.size, self.target.x))

            if self.target.y - self.target.size < 0 or self.target.y + self.target.size > SCREEN_HEIGHT:
                self.target.vy = -self.target.vy
                self.target.y = max(self.target.size, min(SCREEN_HEIGHT - self.target.size, self.target.y))

        # Update all projectiles
        self.projectiles = [p for p in self.projectiles if p.active]

        for proj in self.projectiles:
            # Heat-seeking behavior for homing missiles or when Daddy Power is active
            if (proj.is_homing or self.powerup_active) and self.target and self.target.is_straight:
                dx = self.target.x - proj.x
                dy = self.target.y - proj.y
                distance = math.sqrt(dx * dx + dy * dy)

                if distance > 0:
                    # Daddy Power makes projectiles turn faster
                    turn_rate = 0.5 if self.powerup_active else 0.3
                    speed = self.weapons[self.current_weapon_index].speed
                    if self.powerup_active:
                        speed *= 1.5

                    target_vx = (dx / distance) * speed
                    target_vy = (dy / distance) * speed

                    # Gradually adjust velocity toward target
                    proj.vx += (target_vx - proj.vx) * turn_rate
                    proj.vy += (target_vy - proj.vy) * turn_rate

            # Move projectile
            proj.x += proj.vx
            proj.y += proj.vy

            # Deactivate if out of bounds
            if proj.x < 0 or proj.x > SCREEN_WIDTH or proj.y < 0 or proj.y > SCREEN_HEIGHT:
                proj.active = False

            # Check collision with power-up (Leather Daddy)
            if self.powerup:
                dx = proj.x - self.powerup.x
                dy = proj.y - self.powerup.y
                distance = math.sqrt(dx * dx + dy * dy)

                if distance < self.powerup.size / 2 + PROJECTILE_SIZE / 2:
                    proj.active = False
                    self.powerup = None
                    self.powerup_active = True
                    self.powerup_end_time = time.time() + 10  # 10 seconds of power
                    self.next_powerup_time = time.time() + random.uniform(20, 40)
                    if "powerup" in self.sounds:
                        self.sounds["powerup"].play()

            # Check collision with target
            if self.target:
                dx = proj.x - self.target.x
                dy = proj.y - self.target.y
                distance = math.sqrt(dx * dx + dy * dy)

                if distance < self.target.size + PROJECTILE_SIZE / 2:
                    proj.active = False
                    # Triple points during Daddy Power!
                    self.score += 3 if self.powerup_active else 1

                    weapon = self.weapons[proj.ammo_index]
                    if weapon.hit_sound_path in self.sounds:
                        self.sounds[weapon.hit_sound_path].play()

                    # Respawn target in new location
                    self.target.x = random.uniform(100, SCREEN_WIDTH - 100)
                    self.target.y = random.uniform(100, SCREEN_HEIGHT - 100)
                    self.target.vx = random.uniform(-5, 5)
                    self.target.vy = random.uniform(-5, 5)
                    self.target.is_straight = True  # Keep it straight for Pride Parade

    def draw(self):
        """Draw all game elements"""
        self.screen.fill(BLACK)

        # Draw Leather Daddy power-up with pulsing animation
        if self.powerup:
            pulse = math.sin(time.time() * 10) * 10 + 10

            # Leather brown outer circle
            pygame.draw.circle(self.screen, BROWN,
                             (int(self.powerup.x), int(self.powerup.y)),
                             int(self.powerup.size / 2 + pulse))
            # Black inner circle
            pygame.draw.circle(self.screen, BLACK,
                             (int(self.powerup.x), int(self.powerup.y)),
                             int(self.powerup.size / 2.5))

            # Sparkle effect rotating around power-up
            for i in range(8):
                angle = (time.time() * 5 + i * 45) * math.pi / 180
                sparkle_x = self.powerup.x + math.cos(angle) * (self.powerup.size / 2 + pulse + 10)
                sparkle_y = self.powerup.y + math.sin(angle) * (self.powerup.size / 2 + pulse + 10)
                pygame.draw.circle(self.screen, YELLOW, (int(sparkle_x), int(sparkle_y)), 5)

            # "DADDY" text
            text = self.small_font.render("DADDY", True, WHITE)
            text_rect = text.get_rect(center=(int(self.powerup.x), int(self.powerup.y - 60)))
            self.screen.blit(text, text_rect)

        # Draw target
        if self.target and self.selected_enemy:
            # Adjust position to center the image
            pos_x = int(self.target.x - self.selected_enemy.image.get_width() / 2)
            pos_y = int(self.target.y - self.selected_enemy.image.get_height() / 2)
            self.screen.blit(self.selected_enemy.image, (pos_x, pos_y))

        # Draw projectiles with rainbow effect for homing/powered projectiles
        for proj in self.projectiles:
            ammo_img = self.ammo_images[proj.ammo_index]
            # Adjust position to center the image
            pos_x = int(proj.x - ammo_img.get_width() / 2)
            pos_y = int(proj.y - ammo_img.get_height() / 2)

            if proj.is_homing or self.powerup_active:
                # Apply a rainbow tint to the image
                tinted_image = ammo_img.copy()
                t = time.time() * 10
                r = int((math.sin(t + 0) * 127 + 128) * 0.5)
                g = int((math.sin(t + 2) * 127 + 128) * 0.5)
                b = int((math.sin(t + 4) * 127 + 128) * 0.5)
                tinted_image.fill((r, g, b, 128), special_flags=pygame.BLEND_RGBA_MULT)
                self.screen.blit(tinted_image, (pos_x, pos_y))
            else:
                self.screen.blit(ammo_img, (pos_x, pos_y))

        # Draw aim line when dragging
        if self.is_touching:
            pygame.draw.line(self.screen, (100, 100, 100),
                           (self.weapon_x, SCREEN_HEIGHT - 130),  # Start from weapon position
                           (self.touch_x, self.touch_y), 3)

        # Draw current weapon at bottom - follows cursor horizontally
        weapon_img = self.weapon_images[self.current_weapon_index]
        weapon_display_x = self.weapon_x - 60  # Center the 120px weapon on cursor X
        weapon_display_y = SCREEN_HEIGHT - 270  # Fixed vertical position
        self.screen.blit(weapon_img, (weapon_display_x, weapon_display_y))

        # Add weapon glow effect when aiming
        if self.is_touching:
            glow_surface = pygame.Surface((140, 140), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 255, 0, 80), (70, 70), 70)
            self.screen.blit(glow_surface, (weapon_display_x - 10, weapon_display_y - 10))

        # Draw UI elements
        current_weapon = self.weapons[self.current_weapon_index]

        y_offset = 30
        text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(text, (20, y_offset))

        y_offset += 30
        text = self.small_font.render(f"Weapon: {current_weapon.name}", True, WHITE)
        self.screen.blit(text, (20, y_offset))

        y_offset += 30
        text = self.small_font.render(f"Ammo: {current_weapon.projectile_type}", True, WHITE)
        self.screen.blit(text, (20, y_offset))

        # Show Daddy Power status
        if self.powerup_active:
            y_offset += 30
            time_left = int(self.powerup_end_time - time.time())
            text = self.small_font.render(f"💪 DADDY POWER! {time_left}s", True, GOLD)
            self.screen.blit(text, (20, y_offset))

            y_offset += 30
            text = self.small_font.render("ALL WEAPONS SEEK! 3X POINTS!", True, GOLD)
            self.screen.blit(text, (20, y_offset))

        # Show homing status for Pride Parade and Trans Missile
        elif current_weapon.is_homing and self.target and self.target.is_straight:
            y_offset += 30
            text = self.small_font.render("🎯 SEEKING STRAIGHT TARGET!", True, PINK)
            self.screen.blit(text, (20, y_offset))

        # Instructions at top
        text = self.small_font.render("SPACE: Change Weapon | ESC: Quit", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        self.screen.blit(text, text_rect)

        # Launch area at bottom
        pygame.draw.rect(self.screen, (50, 50, 100),
                        (0, SCREEN_HEIGHT - 150, SCREEN_WIDTH, 150), 0)
        text = self.small_font.render("LAUNCH AREA - Click & Drag to Aim and Fire", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(text, text_rect)

        pygame.display.flip()

    def draw_enemy_selection_screen(self):
        """Draw the enemy selection screen"""
        self.screen.fill(BLACK)
        title_font = pygame.font.Font(None, 72)
        subtitle_font = pygame.font.Font(None, 36)

        # Title
        title_text = title_font.render("CHOOSE YOUR TARGET", True, RED)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH / 2, 60))
        self.screen.blit(title_text, title_rect)

        # Grid layout
        grid_cols = 4
        grid_rows = 2
        col_width = SCREEN_WIDTH // grid_cols
        row_height = (SCREEN_HEIGHT - 150) // grid_rows
        start_x = col_width // 2
        start_y = 150 + row_height // 2

        for i, enemy in enumerate(self.enemies):
            col = i % grid_cols
            row = i // grid_cols
            x = start_x + col * col_width
            y = start_y + row * row_height

            # Draw thumbnail
            thumbnail = pygame.transform.scale(enemy.image, (100, 100))
            thumb_rect = thumbnail.get_rect(center=(x, y - 20))
            self.screen.blit(thumbnail, thumb_rect)

            # Draw name
            try:
                font_path = os.path.join('fonts', enemy.font_path)
                name_font = pygame.font.Font(font_path, 28)
            except:
                name_font = self.small_font

            name_text = name_font.render(enemy.name, True, WHITE)
            name_rect = name_text.get_rect(center=(x, y + 50))
            self.screen.blit(name_text, name_rect)

            # Draw description
            desc_font = pygame.font.Font(None, 20)
            desc_text = desc_font.render(enemy.description, True, (200, 200, 200))
            desc_rect = desc_text.get_rect(center=(x, y + 80))
            self.screen.blit(desc_text, desc_rect)

        pygame.display.flip()

    def handle_enemy_selection_events(self):
        """Handle events on the enemy selection screen"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                grid_cols = 4
                col_width = SCREEN_WIDTH // grid_cols
                start_x = (SCREEN_WIDTH - (grid_cols * col_width)) / 2 + col_width / 2
                start_y = 250

                for i, enemy in enumerate(self.enemies):
                    col = i % grid_cols
                    x = start_x + col * col_width
                    rect = pygame.Rect(x - 60, start_y - 60, 120, 120)
                    if rect.collidepoint(event.pos):
                        self.selected_enemy = enemy
                        self.state = 'playing'
                        self.reset_target()
                        if "select" in self.sounds:
                            self.sounds["select"].play()
                        try:
                            pygame.mixer.music.load(os.path.join('audio', 'music', self.selected_enemy.music_track))
                            pygame.mixer.music.play(-1)
                        except pygame.error:
                            print(f"✗ Could not load music for {self.selected_enemy.name}.")
                        break

    def launch_projectile(self, target_x, target_y):
        """Launch a projectile from weapon position toward target coordinates"""
        start_x = self.weapon_x  # Launch from weapon's current X position
        start_y = SCREEN_HEIGHT - 130  # Launch from weapon height

        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            current_weapon = self.weapons[self.current_weapon_index]
            speed = current_weapon.speed

            if current_weapon.fire_sound_path in self.sounds:
                self.sounds[current_weapon.fire_sound_path].play()

            # Calculate velocity vector
            vx = (dx / distance) * speed
            vy = (dy / distance) * speed

            # Create and add projectile
            proj = Projectile(start_x, start_y, vx, vy, current_weapon.is_homing, self.current_weapon_index)
            self.projectiles.append(proj)

    def handle_events(self):
        """Handle all input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Cycle through weapons
                    self.current_weapon_index = (self.current_weapon_index + 1) % len(self.weapons)
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Only allow launching from bottom area
                if event.pos[1] > SCREEN_HEIGHT - 150:
                    self.is_touching = True
                    self.touch_x, self.touch_y = event.pos
                    self.weapon_x = event.pos[0]  # Update weapon X position

            elif event.type == pygame.MOUSEMOTION:
                # Always update weapon position with mouse X
                self.weapon_x = event.pos[0]

                if self.is_touching:
                    self.touch_x, self.touch_y = event.pos

            elif event.type == pygame.MOUSEBUTTONUP:
                if self.is_touching:
                    self.launch_projectile(self.touch_x, self.touch_y)
                    self.is_touching = False

    def run(self):
        """Main game loop"""
        print("🎮 Stress Relief Target Game Started!")
        print("Controls:")
        print("  - SPACE: Change weapon")
        print("  - Click & Drag in launch area to fire")
        print("  - ESC: Quit")
        print("\nHit the Leather Daddy power-up for DADDY POWER! 💪")

        try:
            pygame.mixer.music.load(os.path.join('audio', 'music', 'selection_screen.ogg'))
            pygame.mixer.music.play(-1)  # Loop indefinitely
        except pygame.error:
            print("✗ Could not load selection screen music.")

        while self.running:
            if self.state == 'enemy_selection':
                self.handle_enemy_selection_events()
                self.draw_enemy_selection_screen()
            elif self.state == 'playing':
                self.handle_events()
                self.update()
                self.draw()

            self.clock.tick(FPS)

        print(f"\n🎯 Final Score: {self.score}")
        print("Thanks for playing!")
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
