from pgzero.rect import Rect
from settings import WIDTH, HEIGHT, COLOR_SKY, SOUND_ENABLED

# Gerencia o desenho e interação do Menu Principal
class MenuManager:
    def __init__(self):
        center_x = WIDTH // 2
        start_y = HEIGHT // 2 - 50
        
        self.start_btn = Rect((center_x - 120, start_y), (240, 50))
        self.sound_btn = Rect((center_x - 120, start_y + 70), (240, 50))
        self.exit_btn = Rect((center_x - 120, start_y + 140), (240, 50))
        
        self.sound_text = f"VOLUME: {'ON' if SOUND_ENABLED else 'OFF'}"

    def draw(self, screen):
        screen.fill(COLOR_SKY)

        screen.draw.text("ALIEN PLATAFORMER", center=(WIDTH//2, 150), fontsize=80, 
                          color="white", shadow=(2, 2))

        self.draw_button(screen, self.start_btn, "INICIAR", (50, 180, 50))
        self.draw_button(screen, self.sound_btn, self.sound_text, (50, 50, 180))
        self.draw_button(screen, self.exit_btn, "SAIR", (180, 50, 50))

    def draw_button(self, screen, rect, text, color):
        screen.draw.filled_rect(rect, color)
        screen.draw.text(text, center=rect.center, fontsize=30, color="white")

    def handle_click(self, pos):
        if self.start_btn.collidepoint(pos):
            return "start"
        if self.sound_btn.collidepoint(pos):
            return "toggle_sound"
        if self.exit_btn.collidepoint(pos):
            return "exit"
        return None