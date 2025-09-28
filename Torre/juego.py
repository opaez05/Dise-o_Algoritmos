"""
hanoi_pygame.py
Mini-juego Torre de Hanoi con Pygame
- Selección de discos (3-8)
- Interacción por clic (origen -> destino)
- Animación del disco (levantar, mover, bajar)
- Auto-solve con animación
- Contador de movimientos y temporizador
"""

import pygame
import sys
import time
from math import copysign

# ----------------- CONFIG -----------------
SCREEN_W, SCREEN_H = 900, 520
BG_COLOR = (30, 30, 40)
UI_PANEL_COLOR = (20, 20, 30)
PEG_COLOR = (180, 180, 200)
BASE_Y = 400
PEG_TOP_Y = 150
PEG_HEIGHT = BASE_Y - PEG_TOP_Y
PEG_WIDTH = 8

PEG_X = [200, 450, 700]

DISK_HEIGHT = 26
MIN_DISKS = 3
MAX_DISKS = 8

# Disk widths: width(size) where size in [1..n] (1 smallest)
MIN_DISK_W = 60
DISK_STEP_W = 20

# Colors for disks
DISK_COLORS = [
    (241, 196, 15),
    (46, 204, 113),
    (52, 152, 219),
    (155, 89, 182),
    (231, 76, 60),
    (230, 126, 34),
    (149, 165, 166),
    (26, 188, 156),
]

FPS = 60

# Animation speed default (pixels per frame)
DEFAULT_SPEED = 8

# ------------------------------------------

pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Torre de Hanoi - Mini Juego")
clock = pygame.time.Clock()

font_large = pygame.font.SysFont("Segoe UI", 28, bold=True)
font_med = pygame.font.SysFont("Segoe UI", 18)
font_small = pygame.font.SysFont("Segoe UI", 14)

# ---------- Helper functions ----------

def disk_width(size):
    """Given disk size (1..n) return pixel width."""
    return MIN_DISK_W + (size - 1) * DISK_STEP_W

def minimal_moves(n):
    return 2 ** n - 1

def solve_moves_gen(n, a, b, c):
    """Yield moves (from_idx, to_idx) using the recursive algorithm."""
    if n == 1:
        yield (a, c)
    else:
        yield from solve_moves_gen(n - 1, a, c, b)
        yield (a, c)
        yield from solve_moves_gen(n - 1, b, a, c)

# ---------- Game state management ----------

class Game:
    def __init__(self, n_disks=4):
        self.n = n_disks
        self.reset()
        self.speed = DEFAULT_SPEED

    def reset(self):
        # pegs: lists where index 0 is bottom, last is top. top popped/appended using pop()/append()
        self.pegs = [list(range(self.n, 0, -1)), [], []]
        self.move_count = 0
        self.start_time = None
        self.running = False  # true after start pressed
        self.selected = None  # index of selected peg for manual move
        self.moving = None    # moving disk dict when animating
        self.auto_queue = []  # list of moves for auto-solve
        self.auto_mode = False
        self.finished = False

    def start(self):
        self.reset()
        self.running = True
        self.start_time = time.time()

    def start_move(self, src, dst):
        """Begin animating a move from src -> dst. Assumes valid."""
        if self.moving is not None:
            return False
        if src == dst:
            return False
        if not self.pegs[src]:
            return False
        # pop disk from source
        L = len(self.pegs[src])
        size = self.pegs[src].pop()  # top disk
        # Compute initial coords (top-left y for rectangle)
        initial_x = PEG_X[src]
        initial_y = BASE_Y - L * DISK_HEIGHT
        target_x = PEG_X[dst]
        target_y = BASE_Y - (len(self.pegs[dst]) + 1) * DISK_HEIGHT

        # set moving disk object
        color = DISK_COLORS[(size - 1) % len(DISK_COLORS)]
        self.moving = {
            "size": size,
            "color": color,
            "x": initial_x,
            "y": initial_y,
            "src": src,
            "dst": dst,
            "target_x": target_x,
            "target_y": target_y,
            "phase": "lift",  # lift -> move -> drop
            "lift_y": 100,    # y to lift to
            "speed": self.speed
        }
        return True

    def complete_current_move(self):
        """Called when animation finishes: push disk to target and increment counters."""
        if not self.moving:
            return
        dst = self.moving["dst"]
        size = self.moving["size"]
        self.pegs[dst].append(size)
        self.moving = None
        self.move_count += 1
        # check finished
        if len(self.pegs[2]) == self.n:
            self.finished = True
            self.auto_mode = False

    def valid_move(self, src, dst):
        """Check if top of src can move to dst."""
        if src == dst:
            return False
        if not self.pegs[src]:
            return False
        top = self.pegs[src][-1]
        if not self.pegs[dst]:
            return True
        return top < self.pegs[dst][-1]


# ---------- Drawing ----------

def draw_board(g: Game):
    screen.fill(BG_COLOR)
    # UI side panel
    panel_w = 220
    pygame.draw.rect(screen, UI_PANEL_COLOR, (SCREEN_W - panel_w, 0, panel_w, SCREEN_H))

    # Title
    title = font_large.render("Torre de Hanoi", True, (250, 250, 250))
    screen.blit(title, (20, 12))

    # Draw pegs (with glass-like rectangle behind)
    for i, x in enumerate(PEG_X):
        # highlight if selected
        if g.selected == i and not g.moving and g.running:
            pygame.draw.rect(screen, (60, 90, 160), (x - 70, PEG_TOP_Y - 10, 140, BASE_Y - PEG_TOP_Y + 40), border_radius=8)
        # stand base
        pygame.draw.rect(screen, (120, 100, 80), (x - 90, BASE_Y + 20, 180, 16), border_radius=6)
        # glowing zone
        pygame.draw.rect(screen, (10, 30, 50), (x - 70, PEG_TOP_Y - 8, 140, BASE_Y - PEG_TOP_Y + 24), 2, border_radius=8)
        # peg
        pygame.draw.rect(screen, PEG_COLOR, (x - PEG_WIDTH//2, PEG_TOP_Y, PEG_WIDTH, PEG_HEIGHT))

    # Draw disks already on pegs
    for pi, peg in enumerate(g.pegs):
        for idx, size in enumerate(peg):
            # idx: 0 bottom ... top at idx=len(peg)-1
            w = disk_width(size)
            x = PEG_X[pi]
            y_top = BASE_Y - (idx + 1) * DISK_HEIGHT
            rect = pygame.Rect(x - w//2, y_top, w, DISK_HEIGHT - 4)
            color = DISK_COLORS[(size - 1) % len(DISK_COLORS)]
            pygame.draw.rect(screen, color, rect, border_radius=6)
            pygame.draw.rect(screen, (40, 40, 40), rect, 2, border_radius=6)

    # Draw moving disk on top if any
    if g.moving:
        md = g.moving
        w = disk_width(md["size"])
        rect = pygame.Rect(md["x"] - w//2, md["y"], w, DISK_HEIGHT - 4)
        pygame.draw.rect(screen, md["color"], rect, border_radius=6)
        pygame.draw.rect(screen, (30, 30, 30), rect, 2, border_radius=6)

    # Right panel info
    panel_x = SCREEN_W - panel_w + 12
    info_y = 70
    lbl = font_med.render(f"Discos: {g.n}", True, (230, 230, 230))
    screen.blit(lbl, (panel_x, info_y))
    info_y += 36
    moves_text = font_med.render(f"Movimientos: {g.move_count}", True, (230, 230, 230))
    screen.blit(moves_text, (panel_x, info_y))
    info_y += 26
    minmoves = minimal_moves(g.n)
    min_text = font_small.render(f"Minimos: {minmoves}", True, (190, 190, 190))
    screen.blit(min_text, (panel_x, info_y))
    info_y += 36
    # Timer
    elapsed = 0
    if g.start_time:
        elapsed = int(time.time() - g.start_time)
    mm = elapsed // 60
    ss = elapsed % 60
    timer_text = font_med.render(f"Tiempo: {mm:02d}:{ss:02d}", True, (230, 230, 230))
    screen.blit(timer_text, (panel_x, info_y))

    # Buttons
    btn_w = 180
    bx = SCREEN_W - panel_w + (panel_w - btn_w)//2
    by = SCREEN_H - 160
    draw_button(bx, by, btn_w, 36, "Auto Solve", (120, 180, 220))
    draw_button(bx, by + 48, btn_w, 36, "Reset", (240, 140, 100))
    draw_button(bx, by + 96, btn_w//2 - 6, 36, "Speed -", (200, 200, 200))
    draw_button(bx + btn_w//2 + 6, by + 96, btn_w//2 - 6, 36, "Speed +", (200, 200, 200))

    # If finished show overlay
    if g.finished:
        s = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        s.fill((0, 0, 0, 160))
        screen.blit(s, (0, 0))
        t = font_large.render("¡Completado! ✅", True, (255, 255, 255))
        screen.blit(t, (SCREEN_W//2 - t.get_width()//2, SCREEN_H//2 - 40))
        info = font_med.render(f"Movimientos: {g.move_count}  Tiempo: {mm:02d}:{ss:02d}", True, (240, 240, 240))
        screen.blit(info, (SCREEN_W//2 - info.get_width()//2, SCREEN_H//2 + 10))

def draw_button(x, y, w, h, text, color):
    # simple rounded rect button
    pygame.draw.rect(screen, color, (x, y, w, h), border_radius=8)
    pygame.draw.rect(screen, (40, 40, 40), (x, y, w, h), 2, border_radius=8)
    txt = font_med.render(text, True, (10, 10, 10))
    screen.blit(txt, (x + w//2 - txt.get_width()//2, y + h//2 - txt.get_height()//2))

def peg_from_pos(mx, my):
    """Return peg index if clicked on or near peg area, else None."""
    for i, x in enumerate(PEG_X):
        if mx > x - 90 and mx < x + 90 and my > PEG_TOP_Y - 10 and my < BASE_Y + 30:
            return i
    return None

def button_hit(mx, my):
    """Return which button was clicked in side panel: 'auto', 'reset', 'speed_minus', 'speed_plus' or None"""
    panel_w = 220
    btn_w = 180
    bx = SCREEN_W - panel_w + (panel_w - btn_w)//2
    by = SCREEN_H - 160
    rect_auto = pygame.Rect(bx, by, btn_w, 36)
    rect_reset = pygame.Rect(bx, by + 48, btn_w, 36)
    rect_speed_minus = pygame.Rect(bx, by + 96, btn_w//2 - 6, 36)
    rect_speed_plus = pygame.Rect(bx + btn_w//2 + 6, by + 96, btn_w//2 - 6, 36)
    if rect_auto.collidepoint(mx, my):
        return "auto"
    if rect_reset.collidepoint(mx, my):
        return "reset"
    if rect_speed_minus.collidepoint(mx, my):
        return "speed_minus"
    if rect_speed_plus.collidepoint(mx, my):
        return "speed_plus"
    return None

# ---------- Animation update ----------

def update_animation(g: Game):
    """Advance moving disk per frame. Non-blocking."""
    if not g.moving:
        return
    md = g.moving
    sp = max(2, md.get("speed", DEFAULT_SPEED))
    # Phase lift
    if md["phase"] == "lift":
        # move y up until lift_y
        if md["y"] > md["lift_y"]:
            md["y"] -= sp
            if md["y"] < md["lift_y"]:
                md["y"] = md["lift_y"]
        else:
            md["phase"] = "move"
    elif md["phase"] == "move":
        # move x toward target_x, keep y at lift_y
        dx = md["target_x"] - md["x"]
        step = sp * 1.25
        if abs(dx) > step:
            md["x"] += copysign(step, dx)
        else:
            md["x"] = md["target_x"]
            md["phase"] = "drop"
    elif md["phase"] == "drop":
        # move y down to target_y
        if md["y"] < md["target_y"]:
            md["y"] += sp
            if md["y"] > md["target_y"]:
                md["y"] = md["target_y"]
        else:
            # finished move
            g.complete_current_move()

# ---------- Main loop / screens ----------

def main():
    state = "menu"  # 'menu' or 'playing'
    chosen_disks = 4
    g = Game(chosen_disks)
    running = True

    while running:
        dt = clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
                break
            if state == "menu":
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_UP:
                        chosen_disks = min(MAX_DISKS, chosen_disks + 1)
                    elif ev.key == pygame.K_DOWN:
                        chosen_disks = max(MIN_DISKS, chosen_disks - 1)
                    elif ev.key == pygame.K_RETURN:
                        # start
                        g = Game(chosen_disks)
                        g.start()
                        state = "playing"
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    mx, my = ev.pos
                    # Basic clickable start area
                    # We'll accept clicking anywhere in center to start for simplicity
                    if SCREEN_W//2 - 120 < mx < SCREEN_W//2 + 120 and SCREEN_H//2 + 40 < my < SCREEN_H//2 + 90:
                        g = Game(chosen_disks)
                        g.start()
                        state = "playing"

            elif state == "playing":
                # global input handling
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    mx, my = ev.pos
                    # Check side buttons
                    btn = button_hit(mx, my)
                    if btn:
                        if btn == "auto":
                            # toggle auto-solve
                            if not g.auto_mode and not g.moving:
                                moves = list(solve_moves_gen(g.n, 0, 1, 2))
                                g.auto_queue = moves
                                g.auto_mode = True
                            else:
                                # cancel auto
                                g.auto_mode = False
                                g.auto_queue = []
                        elif btn == "reset":
                            g = Game(g.n)
                            g.start()
                        elif btn == "speed_minus":
                            g.speed = max(2, g.speed - 2)
                        elif btn == "speed_plus":
                            g.speed = min(30, g.speed + 2)
                        continue

                    # Click on pegs
                    peg_clicked = peg_from_pos(mx, my)
                    if peg_clicked is not None and not g.moving and not g.finished:
                        if g.selected is None:
                            # select if peg has disk
                            if g.pegs[peg_clicked]:
                                g.selected = peg_clicked
                        else:
                            # attempt move selected -> peg_clicked
                            if g.valid_move(g.selected, peg_clicked):
                                # set speed to current value
                                # start animation
                                g.speed = g.speed
                                started = g.start_move(g.selected, peg_clicked)
                                g.selected = None
                                # start_time if not started earlier
                                if g.start_time is None:
                                    g.start_time = time.time()
                            else:
                                # invalid: deselect
                                g.selected = None

                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_r:
                        g = Game(g.n)
                        g.start()
                    if ev.key == pygame.K_ESCAPE:
                        # back to menu
                        state = "menu"
                    if ev.key == pygame.K_PLUS or ev.key == pygame.K_EQUALS:
                        g.speed = min(30, g.speed + 1)
                    if ev.key == pygame.K_MINUS:
                        g.speed = max(2, g.speed - 1)

        # Update animation and auto-solve queue
        if state == "playing":
            # if animating, update animation
            if g.moving:
                # ensure the moving disk speed matches game speed
                g.moving["speed"] = g.speed
                update_animation(g)
            else:
                # if not animating and auto mode on: start next move
                if g.auto_mode and g.auto_queue:
                    mv = g.auto_queue.pop(0)
                    src, dst = mv
                    # verify move validity (should be valid)
                    if g.valid_move(src, dst):
                        g.start_move(src, dst)
                # if queue empty, stop auto_mode
                if g.auto_mode and not g.auto_queue and not g.moving:
                    g.auto_mode = False

        # Drawing
        if state == "menu":
            screen.fill(BG_COLOR)
            title = font_large.render("Torre de Hanoi - Mini Juego", True, (240, 240, 240))
            screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 60))

            instr = font_med.render("Usa flechas arriba/abajo para elegir discos (3-8). Enter para iniciar.", True, (200, 200, 200))
            screen.blit(instr, (SCREEN_W//2 - instr.get_width()//2, 120))
            choice = font_large.render(f"Discos: {chosen_disks}", True, (255, 215, 120))
            screen.blit(choice, (SCREEN_W//2 - choice.get_width()//2, SCREEN_H//2 - 20))

            start_rect = pygame.Rect(SCREEN_W//2 - 120, SCREEN_H//2 + 40, 240, 50)
            pygame.draw.rect(screen, (80, 160, 200), start_rect, border_radius=8)
            st = font_med.render("START", True, (10, 10, 10))
            screen.blit(st, (start_rect.centerx - st.get_width()//2, start_rect.centery - st.get_height()//2))

        elif state == "playing":
            draw_board(g)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
