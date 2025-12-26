import pgzrun
from pgzero.rect import Rect
import settings
from settings import *
from entities import Hero, Slime, Flag
from menu import MenuManager

# Globais
current_state = STATE_MENU
menu = MenuManager()
scroll_x = 0
game_time = 0

player = Hero(100, 0)
platforms = []
scenery = []
enemies = []
flag = None

DEBUG_SHOW_HITBOX = False 

# Inicialização do Nível
def setup_level():
    global flag, game_time
    
    # Reseta o Timer
    game_time = 0
    
    platforms.clear()
    scenery.clear()
    enemies.clear()

    rows = len(LEVEL_MAP)
    cols = len(LEVEL_MAP[0])
    
    for r in range(rows):
        for c in range(cols):
            char = LEVEL_MAP[r][c]
            x = c * TILE_SIZE
            y = r * TILE_SIZE
            center_x = x + TILE_SIZE / 2
            bottom_y = y + TILE_SIZE

            if char == "1":
                # Lógica de Auto-Tiling (Bordas)
                has_left = (c > 0) and (LEVEL_MAP[r][c-1] == "1")
                has_right = (c < cols - 1) and (LEVEL_MAP[r][c+1] == "1")

                sprite_name = "ground_mid"
                if not has_left and has_right: sprite_name = "ground_left"
                elif has_left and not has_right: sprite_name = "ground_right"
                
                scenery.append(Actor(sprite_name, topleft=(x, y)))
                platforms.append(Rect(x, y, TILE_SIZE, TILE_SIZE))
                
            elif char == "E":
                enemies.append(Slime(center_x, bottom_y, 120))
            elif char == "F":
                flag = Flag(center_x, bottom_y)

setup_level()

# Loop Principal de Atualização
def update(dt):
    global current_state, scroll_x, game_time

    if current_state != STATE_GAME:
        return
        
    # Atualiza o Timer
    game_time += dt

    # Entrada (Input)
    dx = 0
    player.is_moving = False
    
    if keyboard.left:
        dx = -MOVE_SPEED
        player.is_moving = True
    if keyboard.right:
        dx = MOVE_SPEED
        player.is_moving = True

    # Física
    player.apply_gravity()
    player.check_vertical_collision(platforms)
    player.move_x(dx, platforms)
    player.update_animation()

    # Rolagem da Câmera
    target_scroll = player.hitbox.centerx - WIDTH / 2
    map_width = len(LEVEL_MAP[0]) * TILE_SIZE
    scroll_x = max(0, min(target_scroll, map_width - WIDTH))
    
    # Lógica de Morte: Cair do mapa
    if player.hitbox.top > HEIGHT:
        current_state = STATE_LOSE
        if settings.SOUND_ENABLED:
            try: 
                sounds.lose.set_volume(0.1)
                sounds.lose.play() 
            except: pass

    # Lógica de Morte: Inimigos
    for e in enemies:
        e.update()
        if player.hitbox.colliderect(e.hitbox):
            current_state = STATE_LOSE
            if settings.SOUND_ENABLED:
                try: 
                    sounds.lose.set_volume(0.1)
                    sounds.lose.play()
                except: pass

    # Lógica de Vitória
    flag.update()
    flag_rect = Rect(flag.mast_sprite.x - 20, flag.mast_sprite.y - 60, 40, 60)
    if player.hitbox.colliderect(flag_rect):
        flag.active = True
        current_state = STATE_WIN
        if settings.SOUND_ENABLED:
            try: 
                sounds.win.set_volume(0.2)
                sounds.win.play()
            except: pass

# Loop de Desenho
def draw():
    if current_state == STATE_MENU:
        menu.draw(screen)
        return

    screen.fill(COLOR_SKY)

    # Cenário
    for s in scenery:
        screen.blit(s.image, (s.x - scroll_x, s.y))
        
    # Inimigos
    for e in enemies:
        screen.blit(e.sprite.image, (e.sprite.x - scroll_x - e.sprite.width//2, e.sprite.y - e.sprite.height))
        if DEBUG_SHOW_HITBOX:
            r = Rect((e.hitbox.x - scroll_x, e.hitbox.y), e.hitbox.size)
            screen.draw.rect(r, (255, 0, 0))

    # Bandeira
    if flag:
        screen.blit(flag.mast_sprite.image, 
                    (flag.mast_sprite.x - scroll_x - flag.mast_sprite.width//2, 
                     flag.mast_sprite.y - flag.mast_sprite.height))
        screen.blit(flag.flag_sprite.image, 
                    (flag.flag_sprite.x - scroll_x - flag.flag_sprite.width//2, 
                     flag.flag_sprite.y - flag.flag_sprite.height))

    # Jogador
    screen.blit(player.sprite.image, 
                (player.sprite.x - scroll_x - player.sprite.width//2, 
                 player.sprite.y - player.sprite.height))
    
    if DEBUG_SHOW_HITBOX:
        r = Rect((player.hitbox.x - scroll_x, player.hitbox.y), player.hitbox.size)
        screen.draw.rect(r, (255, 0, 0))

    # UI: Timer
    screen.draw.text(f"Tempo: {game_time:.1f}s", (20, 20), fontsize=40, color="white", shadow=(1,1))

    # UI: Telas Finais
    if current_state == STATE_WIN:
        screen.draw.text("VITORIA", center=(WIDTH//2, HEIGHT//2 - 20), fontsize=80, color="yellow", shadow=(1,1))
        screen.draw.text(f"Tempo Final: {game_time:.2f}s", center=(WIDTH//2, HEIGHT//2 + 50), fontsize=50, color="white")
        screen.draw.text("Aperte SPACE para jogar novamente", center=(WIDTH//2, HEIGHT//2 + 100), fontsize=30, color="white")
        screen.draw.text("Aperte M para Menu", center=(WIDTH//2, HEIGHT//2 + 150), fontsize=30, color="orange")
    
    if current_state == STATE_LOSE:
        screen.draw.text("DERROTA", center=(WIDTH//2, HEIGHT//2), fontsize=80, color="red", shadow=(1,1))
        screen.draw.text("Aperte SPACE para reiniciar", center=(WIDTH//2, HEIGHT//2 + 60), fontsize=40, color="white")
        screen.draw.text("Aperte M para Menu", center=(WIDTH//2, HEIGHT//2 + 110), fontsize=30, color="orange")

def on_key_down(key):
    global current_state
    
    if current_state == STATE_GAME:
        if key == keys.SPACE and player.on_ground:
            player.vel_y = JUMP_SPEED
            if settings.SOUND_ENABLED:
                try: 
                    sounds.jump.set_volume(0.2)
                    sounds.jump.play()
                except: pass

    elif current_state in (STATE_LOSE, STATE_WIN):
        if key == keys.SPACE:
            setup_level()
            player.hitbox.topleft = (100, 100)
            player.vel_y = 0
            current_state = STATE_GAME
        
        # Botão para voltar ao Menu
        elif key == keys.M:
            current_state = STATE_MENU
            if settings.SOUND_ENABLED:
                try:
                    if not music.is_playing('bg_music'):
                        music.play('bg_music')
                        music.set_volume(0.05)
                except: pass

def on_mouse_down(pos):
    global current_state
    
    if current_state == STATE_MENU:
        action = menu.handle_click(pos)
        
        if action and settings.SOUND_ENABLED:
            try: 
                sounds.click_001.set_volume(0.3)
                sounds.click_001.play()
            except: pass
        
        if action == "start":
            setup_level()
            player.hitbox.topleft = (100, 100)
            current_state = STATE_GAME
            music.stop()
                
        elif action == "toggle_sound":
            settings.SOUND_ENABLED = not settings.SOUND_ENABLED
            menu.sound_text = f"VOLUME: {'ON' if settings.SOUND_ENABLED else 'OFF'}"
            
            if settings.SOUND_ENABLED:
                try: 
                    if not music.is_playing('bg_music'):
                        music.play('bg_music')
                        music.set_volume(0.05)
                except: pass
            else:
                music.stop()
                
        elif action == "exit":
            quit()

if settings.SOUND_ENABLED:
    try:
        music.play('bg_music')
        music.set_volume(0.05)
    except: pass

pgzrun.go()