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
    def __init__(self, name, projectile_type, speed, is_homing=False):
        self.name = name
        self.projectile_type = projectile_type
        self.speed = speed
        self.is_homing = is_homing


class Projectile:
    """Represents a fired projectile"""
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


class Game:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Stress Relief Target Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Initialize weapons with all 12 types
        self.weapons = [
            Weapon("Slingshot", "Vegetables", 15),
            Weapon("Bottle Rockets", "Rockets", 20),
            Weapon("Catapult", "Boulders", 12),
            Weapon("Tomato BB Gun", "Tomatoes", 25),
            Weapon("Poison Bow", "Poison Arrows", 18),
            Weapon("Marshmallow Crossbow", "Flaming Marshmallows", 16),
            Weapon("Darts", "Darts", 22),
            Weapon("Throwing Stars", "Shuriken", 24),
            Weapon("Potato Cannon", "Potatoes", 17),
            Weapon("Frog Cannon", "Gay Frogs", 17),
            Weapon("Trans Missile", "Guided Missile", 10, is_homing=True),
            Weapon("Pride Parade", "Rainbow Seeker", 14, is_homing=True)
        ]

        # Load weapon images (or create placeholders if not found)
        self.weapon_images = {}
        self.load_weapon_images()

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

            # Try multiple paths
            possible_paths = [
                os.path.join('images', 'ammo', filename),
                os.path.join('ammo', filename),
                filename
            ]

            for path in possible_paths:
                try:
                    img = pygame.image.load(path)
                    img = pygame.transform.scale(img, (PROJECTILE_SIZE, PROJECTILE_SIZE))
                    self.ammo_images[i] = img
                    image_loaded = True
                    print(f"✓ Loaded {filename} from {path}")
                    break
                except:
                    continue

            if not image_loaded:
                # Create placeholder if image not found
                print(f"✗ Could not load {filename}, using placeholder")
                surface = pygame.Surface((PROJECTILE_SIZE, PROJECTILE_SIZE), pygame.SRCALPHA)

                # Use yellow circle as placeholder
                pygame.draw.circle(surface, YELLOW, (PROJECTILE_SIZE//2, PROJECTILE_SIZE//2), PROJECTILE_SIZE//2 - 2)
                pygame.draw.circle(surface, BLACK, (PROJECTILE_SIZE//2, PROJECTILE_SIZE//2), PROJECTILE_SIZE//2 - 2, 2)

                self.ammo_images[i] = surface

    def reset_target(self):
        """Reset target to a new random position with random velocity"""
        self.target = Target(
            x=SCREEN_WIDTH / 2,
            y=SCREEN_HEIGHT / 3,
            vx=random.uniform(-4, 4),
            vy=random.uniform(-4, 4),
            size=TARGET_SIZE
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

            # Check collision with target
            if self.target:
                dx = proj.x - self.target.x
                dy = proj.y - self.target.y
                distance = math.sqrt(dx * dx + dy * dy)

                if distance < self.target.size + PROJECTILE_SIZE / 2:
                    proj.active = False
                    # Triple points during Daddy Power!
                    self.score += 3 if self.powerup_active else 1

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

        # Draw target (red bullseye)
        if self.target:
            pygame.draw.circle(self.screen, RED,
                             (int(self.target.x), int(self.target.y)),
                             int(self.target.size))
            pygame.draw.circle(self.screen, WHITE,
                             (int(self.target.x), int(self.target.y)),
                             int(self.target.size * 0.6))
            pygame.draw.circle(self.screen, RED,
                             (int(self.target.x), int(self.target.y)),
                             int(self.target.size * 0.3))

        # Draw projectiles with rainbow effect for homing/powered projectiles
        for proj in self.projectiles:
            if proj.is_homing or self.powerup_active:
                # Animated rainbow color effect
                t = time.time() * 1000
                color = (
                    int((t / 10) % 255),
                    int((t / 15) % 255),
                    int((t / 20) % 255)
                )
            else:
                color = YELLOW

            pygame.draw.circle(self.screen, color,
                             (int(proj.x), int(proj.y)),
                             int(PROJECTILE_SIZE / 2))

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

            # Calculate velocity vector
            vx = (dx / distance) * speed
            vy = (dy / distance) * speed

            # Create and add projectile
            proj = Projectile(start_x, start_y, vx, vy, current_weapon.is_homing)
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

        while self.running:
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
