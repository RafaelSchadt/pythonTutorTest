import random
from pgzero.actor import Actor
from pgzero.rect import Rect
from pgzero.builtins import sounds
import settings 
from settings import GRAVITY, MAX_FALL_SPEED 


# Lógica do Personagem Principal
class Hero:
    def __init__(self, x, y):
        self.sprite = Actor("character_green_idle")
        self.sprite.anchor = ("center", "bottom")
        self.hitbox = Rect(x, y, 40, 100)

        self.idle_frames = ["character_green_idle", "character_green_front"]
        self.walk_frames = ["character_green_walk_a", "character_green_walk_b"]
        
        self.step_sounds = [
            "footstep_grass_000", "footstep_grass_001", 
            "footstep_grass_002", "footstep_grass_003", 
            "footstep_grass_004"
        ]
        
        self.vel_y = 0
        self.on_ground = False
        self.is_moving = False
        self.anim_timer = 0
        self.visual_offset_y = 30

    def update_animation(self):
        self.anim_timer += 1
        
        if not self.on_ground:
            self.sprite.image = "character_green_jump"
        elif self.is_moving:
            frames = self.walk_frames
            self.sprite.image = frames[(self.anim_timer // 8) % len(frames)]
            
            # Toca o som a cada 20 frames
            if self.anim_timer % 20 == 0:
                self.play_step_sound()
        else:
            frames = self.idle_frames
            self.sprite.image = frames[(self.anim_timer // 20) % len(frames)]
        
        self.sprite.pos = (self.hitbox.centerx, self.hitbox.bottom + self.visual_offset_y)

    def play_step_sound(self):
        if settings.SOUND_ENABLED:
            try:
                choice = random.choice(self.step_sounds)
                sfx = getattr(sounds, choice)
                sfx.set_volume(0.1) 
                sfx.play()
            except: pass

    def apply_gravity(self):
        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL_SPEED)
        self.hitbox.y += self.vel_y

    def move_x(self, dx, platforms):
        self.hitbox.x += dx
        for plat in platforms:
            if self.hitbox.colliderect(plat):
                if dx > 0: self.hitbox.right = plat.left
                elif dx < 0: self.hitbox.left = plat.right

    def check_vertical_collision(self, platforms):
        self.on_ground = False
        for plat in platforms:
            if self.hitbox.colliderect(plat):
                if self.vel_y > 0:
                    self.hitbox.bottom = plat.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.hitbox.top = plat.bottom
                    self.vel_y = 0


# Lógica do Inimigo
class Slime:
    def __init__(self, x, y, patrol_dist):
        self.sprite = Actor("slime_normal_walk_a")
        self.sprite.anchor = ("center", "bottom")
        self.hitbox = Rect(x, y - 40, 50, 80)

        self.start_x = x
        self.dist = patrol_dist
        self.dir = 1

        self.walk_frames = ["slime_normal_walk_a", "slime_normal_walk_b"]
        self.idle_frames = ["slime_normal_rest", "slime_normal_flat"]

        self.state = "walk"   # walk | idle
        self.timer = 0
        self.visual_offset_y = 0

    def update(self):
        self.timer += 1

        if self.state == "walk":
            self.hitbox.x += self.dir * 2

            # anima andando
            self.sprite.image = self.walk_frames[(self.timer // 10) % 2]

            # chegou no limite da patrulha → entra em idle
            if abs(self.hitbox.x - self.start_x) >= self.dist:
                self.state = "idle"
                self.timer = 0

        else:  # idle
            self.sprite.image = self.idle_frames[(self.timer // 20) % 2]

            # fica parado ~1 segundo (60 frames) e volta a andar
            if self.timer >= 60:
                self.dir *= -1
                self.state = "walk"
                self.timer = 0

        self.sprite.pos = (self.hitbox.centerx,
                           self.hitbox.bottom + self.visual_offset_y)


# Lógica da Bandeira de Vitória
class Flag:
    def __init__(self, x, y):
        self.mast_sprite = Actor("flag_off") 
        self.mast_sprite.anchor = ("center", "bottom")
        self.mast_sprite.pos = (x, y + 40)

        self.flag_sprite = Actor("flag_red_a") 
        self.flag_sprite.anchor = ("center", "bottom")
        self.flag_sprite.pos = (x, y - 15)

        self.frames = ["flag_red_a", "flag_red_b"]
        self.active = False
        self.timer = 0

    def update(self):
        self.timer += 1
        self.flag_sprite.image = self.frames[(self.timer // 15) % 2]