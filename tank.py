import tkinter as tk
from tkinter import font as tkfont
import random
import sys

WIDTH = 900
HEIGHT = 640
HUD_HEIGHT = 60
PLAY_HEIGHT = HEIGHT - HUD_HEIGHT
TANK_SIZE = 32
BULLET_SIZE = 7
BLOCK_SIZE = 40
FPS = 45

# 高级扁平化科技风色彩方案
COLORS = {
    "bg_dark": "#111827",          # 极深墨蓝（主战场背景）
    "bg_light": "#1f2937",         # 深灰蓝
    "grid": "#374151",             # 科技感网格线
    "hud": "#0f172a",              # 顶部HUD深邃星空底色
    "hud_border": "#1e293b",       # HUD下边框
    "hud_accent": "#38bdf8",       # 炫酷全息蓝（点缀线）
    "hud_text": "#f8fafc",         # 纯白高亮核心数字
    "hud_muted": "#94a3b8",        # 优雅淡蓝灰（标签文字）
    "panel_bg": "#1e293b",         # HUD数据面板气泡背景
    "panel_border": "#334155",     # 气泡边框
    "player": "#22c55e",           # 荧光翠绿（玩家）
    "player_dark": "#16a34a",
    "player_track": "#f59e0b",     # 琥珀黄履带
    "enemy_normal": "#ef4444",     # 警告红（普通敌军）
    "enemy_fast": "#eab308",       # 活力黄（速度型）
    "enemy_heavy": "#a855f7",      # 魅惑紫（重装战车）
    "brick": "#b45309",            # 砖墙
    "brick_light": "#f59e0b",
    "brick_dark": "#78350f",
    "steel": "#94a3b8",            # 强化合金钢
    "steel_hi": "#cbd5e1",
    "steel_lo": "#475569",
    "bullet_player": "#4ade80",    # 极光绿等离子弹
    "bullet_enemy": "#f43f5e",     # 脉冲红敌弹
    "base": "#3b82f6",             # 玩家基地全息蓝
    "base_dark": "#1d4ed8",
    "power_health": "#06b6d4",     # 道具：医疗
    "power_rapid": "#38bdf8",      # 道具：速射
    "power_shield": "#ec4899",     # 道具：护盾
    "power_power": "#facc15",      # 道具：重炮
    "shadow": "#030712",
}

# 辅助环境检测
def is_mobile():
    try:
        import platform
        if "android" in platform.platform().lower() or "iphone" in platform.platform().lower():
            return True
    except Exception:
        pass
    try:
        import os
        ua = os.environ.get("HTTP_USER_AGENT", "")
        return any(agent in ua for agent in ["Android", "iPhone", "iPad", "iPod", "Mobile"])
    except Exception:
        return False

def set_mobile_orientation(window):
    if is_mobile():
        window.geometry(f"{HEIGHT}x{WIDTH}")
        window.minsize(HEIGHT, WIDTH)
        window.maxsize(HEIGHT, WIDTH)
        window.update_idletasks()

def is_mobile_env():
    import platform
    return any(p in platform.system().lower() for p in ["android", "ios", "iphone", "ipad"])


class TankGame:
    def __init__(self):
        self.window = tk.Tk()
        # 【完美修复】遵照图二效果，将标题直接赋予系统窗口顶部！
        self.window.title("孩子们别忘了骑士梦！")
        self.window.resizable(False, False)
        self.window.configure(bg=COLORS["hud"])
        set_mobile_orientation(self.window)

        # 字体精致化定义
        self.label_font = tkfont.Font(family="Microsoft YaHei UI", size=9, weight="bold")
        self.num_font = tkfont.Font(family="Consolas", size=13, weight="bold")
        self.title_font = tkfont.Font(family="Microsoft YaHei UI", size=11, weight="bold")
        self.big_font = tkfont.Font(family="Microsoft YaHei UI", size=28, weight="bold")
        self.small_font = tkfont.Font(family="Microsoft YaHei UI", size=9)

        self.canvas = tk.Canvas(
            self.window,
            bg=COLORS["bg_dark"],
            width=WIDTH,
            height=HEIGHT,
            highlightthickness=0,
        )
        self.canvas.pack()

        # 重新开始按钮美化
        self.restart_btn = tk.Button(
            self.window,
            text="重新开始 (R)",
            font=("Microsoft YaHei UI", 12, "bold"),
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            relief="flat",
            padx=24,
            pady=6,
            cursor="hand2",
            command=self.restart,
        )
        self.restart_window = None

        self.keys = {"w": False, "s": False, "a": False, "d": False, "space": False}
        self.window.bind("<KeyPress>", self.press)
        self.window.bind("<KeyRelease>", self.release)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.new_game()
        self.game_loop()
        self.window.mainloop()

    def new_game(self):
        self.hide_restart_button()
        self.reset_state()
        self.init_map()
        self.start_wave()
        self.window.focus_force()

    def reset_state(self):
        self.game_over = False
        self.paused = False
        self.score = 0
        self.wave = 0
        self.lives = 3
        self.combo = 0
        self.combo_timer = 0
        self.bullet_cooldown = 0
        self.rapid_timer = 0
        self.shield_timer = 0
        self.power_timer = 0
        self.frame = 0
        self.keys = {"w": False, "s": False, "a": False, "d": False, "space": False}

        self.player = self.make_player()
        self.enemies = []
        self.bullets = []
        self.walls = []
        self.powerups = []
        self.explosions = []
        self.base = {
            "x": WIDTH // 2 - BLOCK_SIZE // 2,
            "y": PLAY_HEIGHT - BLOCK_SIZE - 6,
            "hp": 3,
        }

    def make_player(self):
        return {
            "x": WIDTH // 2 - TANK_SIZE // 2,
            "y": PLAY_HEIGHT - TANK_SIZE * 3,
            "dir": "U",
            "speed": 5,
            "hp": 3,
            "max_hp": 3,
            "damage": 1,
        }

    def safe_zones(self):
        px = self.player["x"] + TANK_SIZE // 2
        py = self.player["y"] + TANK_SIZE // 2
        bx = self.base["x"] + BLOCK_SIZE // 2
        by = self.base["y"] + BLOCK_SIZE // 2
        return [
            (px - 120, py - 90, 240, 180),
            (bx - 90, by - 70, 180, 130),
            (40, 40, WIDTH - 80, 100),
        ]

    def in_safe_zone(self, x, y, w, h):
        for sx, sy, sw, sh in self.safe_zones():
            if self.rect_overlap(x, y, w, h, sx, sy, sw, sh):
                return True
        return False

    def init_map(self):
        self.walls = []
        cols = WIDTH // BLOCK_SIZE
        rows = PLAY_HEIGHT // BLOCK_SIZE

        for c in range(cols):
            if c in (0, cols - 1):
                for r in range(rows):
                    self.walls.append(
                        {"x": c * BLOCK_SIZE, "y": r * BLOCK_SIZE, "type": "steel", "hp": 999}
                    )

        clusters = [
            (2, 3), (5, 2), (8, 4), (11, 3), (14, 2), (17, 4), (20, 3),
            (3, 6), (7, 7), (12, 6), (16, 7), (19, 5),
            (4, 9), (9, 10), (15, 9), (18, 11),
        ]
        for col, row in clusters:
            if col >= cols - 1 or row >= rows - 4:
                continue
            wx, wy = col * BLOCK_SIZE, row * BLOCK_SIZE
            if self.in_safe_zone(wx, wy, BLOCK_SIZE, BLOCK_SIZE):
                continue
            wall_type = "steel" if random.random() < 0.18 else "brick"
            hp = 999 if wall_type == "steel" else 2
            self.walls.append({"x": wx, "y": wy, "type": wall_type, "hp": hp})

        base_x, base_y = self.base["x"], self.base["y"]
        for dx in (-BLOCK_SIZE, BLOCK_SIZE):
            self.walls.append(
                {"x": base_x + dx, "y": base_y, "type": "brick", "hp": 2}
            )

    def start_wave(self):
        self.wave += 1
        count = min(2 + self.wave, 8)
        for _ in range(count):
            self.spawn_enemy()
        if self.wave % 4 == 0:
            self.spawn_enemy("heavy", boss=True)

    def spawn_enemy(self, kind=None, boss=False):
        cols = WIDTH // BLOCK_SIZE
        for _ in range(30):
            ex = random.randint(2, cols - 3) * BLOCK_SIZE
            ey = random.randint(1, 2) * BLOCK_SIZE
            occupied = any(
                self.rect_overlap(ex, ey, TANK_SIZE, TANK_SIZE, e["x"], e["y"], TANK_SIZE, TANK_SIZE)
                for e in self.enemies
            )
            if not occupied and not self.check_wall_collision(ex, ey):
                break
        else:
            ex, ey = WIDTH // 2 - TANK_SIZE // 2, 40

        if boss:
            kind = "heavy"
        elif kind is None:
            roll = random.random()
            kind = "normal" if roll < 0.55 else ("fast" if roll < 0.8 else "heavy")

        presets = {
            "normal": {"speed": 3, "hp": 1, "cooldown": 35, "score": 100, "color": COLORS["enemy_normal"]},
            "fast": {"speed": 5, "hp": 1, "cooldown": 25, "score": 150, "color": COLORS["enemy_fast"]},
            "heavy": {"speed": 2, "hp": 3 if boss else 2, "cooldown": 20, "score": 250 if boss else 180, "color": COLORS["enemy_heavy"]},
        }
        cfg = presets[kind]
        self.enemies.append(
            {
                "x": ex,
                "y": ey,
                "dir": "D",
                "kind": kind,
                "boss": boss,
                "speed": cfg["speed"],
                "hp": cfg["hp"],
                "max_hp": cfg["hp"],
                "cooldown": random.randint(10, cfg["cooldown"]),
                "score": cfg["score"] * (2 if boss else 1),
                "color": cfg["color"],
            }
        )

    def press(self, event):
        key = event.keysym.lower()
        if key in ("w", "up"):
            self.keys["w"] = True
        elif key in ("s", "down"):
            self.keys["s"] = True
        elif key in ("a", "left"):
            self.keys["a"] = True
        elif key in ("d", "right"):
            self.keys["d"] = True
        if event.keysym == "space":
            self.keys["space"] = True
        if key == "p" and not self.game_over:
            self.paused = not self.paused
        if self.game_over and key in ("r", "return", "space"):
            self.restart()

    def release(self, event):
        key = event.keysym.lower()
        if key in ("w", "up"):
            self.keys["w"] = False
        elif key in ("s", "down"):
            self.keys["s"] = False
        elif key in ("a", "left"):
            self.keys["a"] = False
        elif key in ("d", "right"):
            self.keys["d"] = False
        if event.keysym == "space":
            self.keys["space"] = False

    def on_canvas_click(self, _event):
        if self.game_over:
            self.restart()

    def restart(self):
        self.new_game()

    def show_restart_button(self):
        if self.restart_window is not None:
            self.canvas.delete(self.restart_window)
        self.restart_window = self.canvas.create_window(
            WIDTH // 2,
            HEIGHT // 2 + 80,
            window=self.restart_btn,
        )

    def hide_restart_button(self):
        if self.restart_window is not None:
            self.canvas.delete(self.restart_window)
            self.restart_window = None

    def game_loop(self):
        if not self.game_over and not self.paused:
            self.frame += 1
            self.update_timers()
            self.update_player()
            self.update_enemies()
            self.update_bullets()
            self.update_powerups()
            self.update_explosions()
            self.check_collisions()
            self.check_wave_clear()

        self.render()
        self.window.after(1000 // FPS, self.game_loop)

    def update_timers(self):
        for timer_name in ("bullet_cooldown", "rapid_timer", "shield_timer", "power_timer", "combo_timer"):
            value = getattr(self, timer_name)
            if value > 0:
                setattr(self, timer_name, value - 1)
        if self.combo_timer == 0:
            self.combo = 0

    def check_wave_clear(self):
        if not self.enemies and not self.game_over:
            self.start_wave()

    def rect_overlap(self, x1, y1, w1, h1, x2, y2, w2, h2):
        return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2

    def check_wall_collision(self, next_x, next_y, size=TANK_SIZE):
        temp = {"x": next_x, "y": next_y}
        for w in self.walls:
            if self.is_collide(temp, size, w, BLOCK_SIZE):
                return True
        return False

    def update_player(self):
        next_x, next_y = self.player["x"], self.player["y"]
        moved = False

        if self.keys["w"]:
            next_y -= self.player["speed"]
            self.player["dir"] = "U"
            moved = True
        elif self.keys["s"]:
            next_y += self.player["speed"]
            self.player["dir"] = "D"
            moved = True

        if not moved:
            if self.keys["a"]:
                next_x -= self.player["speed"]
                self.player["dir"] = "L"
            elif self.keys["d"]:
                next_x += self.player["speed"]
                self.player["dir"] = "R"

        if 0 <= next_x <= WIDTH - TANK_SIZE and 0 <= next_y <= PLAY_HEIGHT - TANK_SIZE:
            if not self.check_wall_collision(next_x, next_y):
                self.player["x"], self.player["y"] = next_x, next_y

        fire_rate = 4 if self.rapid_timer > 0 else 10
        if self.keys["space"] and self.bullet_cooldown == 0:
            self.shoot(self.player, "player")
            self.bullet_cooldown = fire_rate

    def update_enemies(self):
        for e in self.enemies:
            if random.random() < 0.035:
                e["dir"] = random.choice(["U", "D", "L", "R"])

            next_x, next_y = e["x"], e["y"]
            if e["dir"] == "U":
                next_y -= e["speed"]
            elif e["dir"] == "D":
                next_y += e["speed"]
            elif e["dir"] == "L":
                next_x -= e["speed"]
            elif e["dir"] == "R":
                next_x += e["speed"]

            if (
                0 <= next_x <= WIDTH - TANK_SIZE
                and 0 <= next_y <= PLAY_HEIGHT - TANK_SIZE
                and not self.check_wall_collision(next_x, next_y)
            ):
                e["x"], e["y"] = next_x, next_y
            else:
                e["dir"] = random.choice(["U", "D", "L", "R"])

            if e["cooldown"] > 0:
                e["cooldown"] -= 1
            elif random.random() < 0.025:
                self.shoot(e, "enemy")
                e["cooldown"] = 25 if e["kind"] == "fast" else 18

    def shoot(self, tank, bullet_type):
        bx = tank["x"] + TANK_SIZE // 2
        by = tank["y"] + TANK_SIZE // 2
        speed = 11 if bullet_type == "player" else 8
        damage = self.player["damage"] if bullet_type == "player" else 1
        self.bullets.append(
            {
                "x": bx,
                "y": by,
                "dir": tank["dir"],
                "type": bullet_type,
                "speed": speed,
                "damage": damage,
            }
        )

    def update_bullets(self):
        for b in self.bullets[:]:
            if b["dir"] == "U":
                b["y"] -= b["speed"]
            elif b["dir"] == "D":
                b["y"] += b["speed"]
            elif b["dir"] == "L":
                b["x"] -= b["speed"]
            elif b["dir"] == "R":
                b["x"] += b["speed"]

            if b["x"] < 0 or b["x"] > WIDTH or b["y"] < 0 or b["y"] > PLAY_HEIGHT:
                if b in self.bullets:
                    self.bullets.remove(b)

    def update_powerups(self):
        for p in self.powerups[:]:
            p["life"] -= 1
            if p["life"] <= 0:
                self.powerups.remove(p)

    def update_explosions(self):
        for ex in self.explosions[:]:
            ex["life"] -= 1
            ex["radius"] += 1.4
            if ex["life"] <= 0:
                self.explosions.remove(ex)

    def add_explosion(self, x, y, big=False):
        self.explosions.append({"x": x, "y": y, "radius": 5, "life": 12 if big else 8})

    def spawn_powerup(self, x, y):
        if random.random() > 0.35:
            return
        kind = random.choice(["health", "rapid", "shield", "power"])
        self.powerups.append({"x": x, "y": y, "kind": kind, "life": FPS * 12})

    def apply_powerup(self, kind):
        if kind == "health":
            self.player["hp"] = min(self.player["max_hp"], self.player["hp"] + 1)
        elif kind == "rapid":
            self.rapid_timer = FPS * 8
        elif kind == "shield":
            self.shield_timer = FPS * 6
        elif kind == "power":
            self.power_timer = FPS * 10
            self.player["damage"] = 2

    def is_collide(self, obj1, size1, obj2, size2):
        return self.rect_overlap(obj1["x"], obj1["y"], size1, size1, obj2["x"], obj2["y"], size2, size2)

    def damage_player(self):
        if self.shield_timer > 0:
            return
        self.player["hp"] -= 1
        self.add_explosion(self.player["x"] + TANK_SIZE // 2, self.player["y"] + TANK_SIZE // 2)
        if self.player["hp"] <= 0:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self.player = self.make_player()
                self.player["damage"] = 2 if self.power_timer > 0 else 1
                self.shield_timer = FPS * 2

    def kill_enemy(self, enemy, bullet):
        enemy["hp"] -= bullet["damage"]
        if enemy["hp"] > 0:
            return False

        self.enemies.remove(enemy)
        self.add_explosion(enemy["x"] + TANK_SIZE // 2, enemy["y"] + TANK_SIZE // 2, big=enemy.get("boss", False))
        self.combo += 1
        self.combo_timer = FPS * 3
        self.score += enemy["score"] + self.combo * 20
        self.spawn_powerup(enemy["x"], enemy["y"])
        return True

    def check_collisions(self):
        for b in self.bullets[:]:
            removed = False

            for w in self.walls[:]:
                if self.is_collide(b, BULLET_SIZE, w, BLOCK_SIZE):
                    if w["type"] != "steel":
                        w["hp"] -= b["damage"]
                        if w["hp"] <= 0:
                            self.walls.remove(w)
                            self.add_explosion(w["x"] + BLOCK_SIZE // 2, w["y"] + BLOCK_SIZE // 2)
                    if b in self.bullets:
                        self.bullets.remove(b)
                    removed = True
                    break
            if removed:
                continue

            if self.is_collide(b, BULLET_SIZE, self.base, BLOCK_SIZE):
                self.base["hp"] -= b["damage"]
                self.add_explosion(b["x"], b["y"], big=True)
                if b in self.bullets:
                    self.bullets.remove(b)
                if self.base["hp"] <= 0:
                    self.game_over = True
                continue

            if b["type"] == "player":
                for e in self.enemies[:]:
                    if self.is_collide(b, BULLET_SIZE, e, TANK_SIZE):
                        if self.kill_enemy(e, b):
                            if b in self.bullets:
                                self.bullets.remove(b)
                        removed = True
                        break
            elif b["type"] == "enemy":
                if self.is_collide(b, BULLET_SIZE, self.player, TANK_SIZE):
                    if b in self.bullets:
                        self.bullets.remove(b)
                    self.damage_player()

        for p in self.powerups[:]:
            pickup = {"x": self.player["x"], "y": self.player["y"]}
            if self.is_collide(pickup, TANK_SIZE, p, 22):
                self.apply_powerup(p["kind"])
                self.powerups.remove(p)

        if self.power_timer == 0:
            self.player["damage"] = 1

    def draw_background(self):
        for row in range(HUD_HEIGHT, HEIGHT, BLOCK_SIZE):
            for col in range(0, WIDTH, BLOCK_SIZE):
                color = COLORS["bg_dark"] if ((col + row) // BLOCK_SIZE) % 2 == 0 else COLORS["bg_light"]
                self.canvas.create_rectangle(col, row, col + BLOCK_SIZE, row + BLOCK_SIZE, fill=color, outline="")
        for x in range(0, WIDTH, BLOCK_SIZE):
            self.canvas.create_line(x, HUD_HEIGHT, x, HEIGHT, fill=COLORS["grid"])
        for y in range(HUD_HEIGHT, HEIGHT, BLOCK_SIZE):
            self.canvas.create_line(0, y, WIDTH, y, fill=COLORS["grid"])

    # 【核心UI优化】重写顶部面板，移除错位文字，换用高科技磨砂气泡卡片加进度条血条
    def draw_hud(self):
        # 顶部HUD底座
        self.canvas.create_rectangle(0, 0, WIDTH, HUD_HEIGHT, fill=COLORS["hud"], outline=COLORS["hud_border"], width=1)
        self.canvas.create_line(0, HUD_HEIGHT - 1, WIDTH, HUD_HEIGHT - 1, fill=COLORS["hud_accent"], width=2)

        # 1. 普通数据气泡卡片
        panels = [
            (16, 100, f"{self.score:05d}", "SCORE"),
            (132, 80, f"{self.wave}", "WAVE"),
            (228, 80, f"X{self.combo}", "COMBO"),
            (324, 70, f"{self.lives}", "LIVES"),
        ]
        for px, pw, value, label in panels:
            # 扁平圆角卡片矩形
            self.canvas.create_rectangle(px, 12, px + pw, HUD_HEIGHT - 12, fill=COLORS["panel_bg"], outline=COLORS["panel_border"], width=1)
            # 数据居中精密排列
            cx = px + pw // 2
            self.canvas.create_text(cx, 22, text=label, fill=COLORS["hud_muted"], font=self.label_font)
            self.canvas.create_text(cx, 38, text=value, fill=COLORS["hud_text"], font=self.num_font)

        # 2. 炫酷科技血条（代替原先简陋的爱心文字）
        hp_x = 410
        hp_w = 140
        self.canvas.create_rectangle(hp_x, 12, hp_x + hp_w, HUD_HEIGHT - 12, fill=COLORS["panel_bg"], outline=COLORS["panel_border"], width=1)
        self.canvas.create_text(hp_x + 30, 30, text="HP", fill="#f43f5e", font=self.num_font)
        
        # 绘制生命值血条矩形
        bar_x1 = hp_x + 55
        bar_w = 70
        bar_y1 = 23
        bar_h = 13
        # 血条背景槽
        self.canvas.create_rectangle(bar_x1, bar_y1, bar_x1 + bar_w, bar_y1 + bar_h, fill="#0f172a", outline="#334155")
        if self.player["hp"] > 0:
            ratio = self.player["hp"] / self.player["max_hp"]
            hp_color = "#22c55e" if ratio > 0.4 else "#ef4444"
            self.canvas.create_rectangle(bar_x1 + 1, bar_y1 + 1, bar_x1 + int(bar_w * ratio) - 1, bar_y1 + bar_h - 1, fill=hp_color, outline="")

        # 3. 动态状态卡片（状态Buff指示灯）
        buffs = []
        if self.rapid_timer > 0: buffs.append(("RAPID", COLORS["power_rapid"]))
        if self.shield_timer > 0: buffs.append(("SHIELD", COLORS["power_shield"]))
        if self.power_timer > 0: buffs.append(("POWER", COLORS["power_power"]))
        
        bx = 566
        self.canvas.create_rectangle(bx, 12, bx + 160, HUD_HEIGHT - 12, fill=COLORS["panel_bg"], outline=COLORS["panel_border"], width=1)
        self.canvas.create_text(bx + 12, 30, text="STATUS", fill=COLORS["hud_muted"], font=self.label_font, anchor="w")
        
        if not buffs:
            self.canvas.create_text(bx + 75, 30, text="READY", fill="#64748b", font=self.label_font, anchor="w")
        else:
            # 动态显示第一个当前获得的增益
            active_buff, b_color = buffs[0]
            self.canvas.create_rectangle(bx + 75, 20, bx + 145, 40, fill="#0f172a", outline=b_color)
            self.canvas.create_text(bx + 110, 30, text=active_buff, fill=b_color, font=self.label_font, anchor="c")

        # 右侧操作提示改小，低调对齐
        self.canvas.create_text(
            WIDTH - 16,
            HUD_HEIGHT // 2,
            text="PC: WASD + SPACE\nMobile: 竖屏触控",
            anchor="e",
            fill=COLORS["hud_muted"],
            font=self.small_font,
            justify="right"
        )

    def draw_wall(self, wall):
        x, y = wall["x"], wall["y"] + HUD_HEIGHT
        if wall["type"] == "steel":
            self.canvas.create_rectangle(x, y, x + BLOCK_SIZE, y + BLOCK_SIZE, fill=COLORS["steel_lo"], outline=COLORS["steel_lo"])
            self.canvas.create_rectangle(x + 3, y + 3, x + BLOCK_SIZE - 3, y + BLOCK_SIZE - 3, fill=COLORS["steel"], outline=COLORS["steel_hi"], width=2)
            self.canvas.create_line(x + 8, y + 8, x + BLOCK_SIZE - 8, y + BLOCK_SIZE - 8, fill=COLORS["steel_hi"])
            self.canvas.create_line(x + BLOCK_SIZE - 8, y + 8, x + 8, y + BLOCK_SIZE - 8, fill=COLORS["steel_hi"])
        else:
            color = COLORS["brick"] if wall["hp"] >= 2 else COLORS["brick_light"]
            self.canvas.create_rectangle(x, y, x + BLOCK_SIZE, y + BLOCK_SIZE, fill=COLORS["brick_dark"], outline="")
            self.canvas.create_rectangle(x + 2, y + 2, x + BLOCK_SIZE - 2, y + BLOCK_SIZE - 2, fill=color, outline=COLORS["brick_dark"])
            self.canvas.create_line(x + 2, y + 2, x + BLOCK_SIZE - 2, y + 2, fill=COLORS["brick_light"], width=2)
            for i in range(4):
                bx = x + (i % 2) * (BLOCK_SIZE // 2)
                by = y + (i // 2) * (BLOCK_SIZE // 2)
                self.canvas.create_rectangle(bx + 3, by + 8, bx + BLOCK_SIZE // 2 - 3, by + BLOCK_SIZE // 2 - 3, outline=COLORS["brick_dark"])

    def draw_base(self):
        x, y = self.base["x"], self.base["y"] + HUD_HEIGHT
        self.canvas.create_rectangle(x - 4, y - 4, x + BLOCK_SIZE + 4, y + BLOCK_SIZE + 4, fill=COLORS["base_dark"], outline="")
        self.canvas.create_rectangle(x, y, x + BLOCK_SIZE, y + BLOCK_SIZE, fill=COLORS["base"], outline="#a5d6a7", width=2)
        self.canvas.create_polygon(
            x + BLOCK_SIZE // 2,
            y + 10,
            x + BLOCK_SIZE - 10,
            y + BLOCK_SIZE - 8,
            x + 10,
            y + BLOCK_SIZE - 8,
            fill=COLORS["base_dark"],
            outline="#c8e6c9",
        )
        self.canvas.create_text(x + BLOCK_SIZE // 2, y + BLOCK_SIZE // 2 + 12, text="BASE", fill="white", font=("Arial", 9, "bold"))

    def draw_tank(self, tank, is_player=False):
        x, y = tank["x"], tank["y"] + HUD_HEIGHT
        d = tank["dir"]
        body = COLORS["player"] if is_player else tank.get("color", COLORS["enemy_normal"])
        body_dark = COLORS["player_dark"] if is_player else "#8e0000"
        track = COLORS["player_track"]

        self.canvas.create_oval(x + 4, y + TANK_SIZE - 6, x + TANK_SIZE - 4, y + TANK_SIZE + 2, fill=COLORS["shadow"], outline="")

        if is_player and self.shield_timer > 0 and self.frame % 8 < 4:
            self.canvas.create_oval(x - 8, y - 8, x + TANK_SIZE + 8, y + TANK_SIZE + 8, outline="#ce93d8", width=3)

        self.canvas.create_rectangle(x + 1, y + 4, x + 7, y + TANK_SIZE - 4, fill=track, outline="#4e342e")
        self.canvas.create_rectangle(x + TANK_SIZE - 7, y + 4, x + TANK_SIZE - 1, y + TANK_SIZE - 4, fill=track, outline="#4e342e")
        self.canvas.create_rectangle(x + 6, y + 6, x + TANK_SIZE - 6, y + TANK_SIZE - 6, fill=body_dark, outline="#263238")
        self.canvas.create_rectangle(x + 8, y + 8, x + TANK_SIZE - 8, y + TANK_SIZE - 8, fill=body, outline="#37474f")

        cx, cy = x + TANK_SIZE // 2, y + TANK_SIZE // 2
        barrel_len = 15 if not tank.get("boss") else 18
        if d == "U":
            self.canvas.create_line(cx, cy, cx, y - barrel_len, fill="#eceff1", width=5)
        elif d == "D":
            self.canvas.create_line(cx, cy, cx, y + TANK_SIZE + barrel_len, fill="#eceff1", width=5)
        elif d == "L":
            self.canvas.create_line(cx, cy, x - barrel_len, cy, fill="#eceff1", width=5)
        elif d == "R":
            self.canvas.create_line(cx, cy, x + TANK_SIZE + barrel_len, cy, fill="#eceff1", width=5)

        if not is_player and tank["hp"] < tank["max_hp"]:
            ratio = tank["hp"] / tank["max_hp"]
            self.canvas.create_rectangle(x, y - 8, x + TANK_SIZE, y - 4, fill="#37474f", outline="")
            self.canvas.create_rectangle(x, y - 8, x + TANK_SIZE * ratio, y - 4, fill="#ff5252", outline="")

        if tank.get("boss"):
            self.canvas.create_text(cx, y - 14, text="BOSS", fill="#ffcdd2", font=("Arial", 9, "bold"))

    def draw_bullet(self, bullet):
        x, y = bullet["x"], bullet["y"] + HUD_HEIGHT
        r = BULLET_SIZE // 2 + (1 if bullet.get("damage", 1) > 1 else 0)
        color = COLORS["bullet_player"] if bullet["type"] == "player" else COLORS["bullet_enemy"]
        self.canvas.create_oval(x - r - 2, y - r - 2, x + r + 2, y + r + 2, outline=color, width=1)
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="white" if bullet["type"] == "player" else "#d84315")

    def draw_powerup(self, power):
        x, y = power["x"], power["y"] + HUD_HEIGHT
        colors = {
            "health": COLORS["power_health"],
            "rapid": COLORS["power_rapid"],
            "shield": COLORS["power_shield"],
            "power": COLORS["power_power"],
        }
        labels = {"health": "+", "rapid": "R", "shield": "S", "power": "P"}
        pulse = 2 if self.frame % 16 < 8 else 0
        c = colors[power["kind"]]
        self.canvas.create_oval(x - pulse, y - pulse, x + 22 + pulse, y + 22 + pulse, outline=c, width=2)
        self.canvas.create_oval(x + 1, y + 1, x + 21, y + 21, fill=c, outline="white", width=2)
        self.canvas.create_text(x + 11, y + 11, text=labels[power["kind"]], fill="#102027", font=("Arial", 10, "bold"))

    def draw_explosion(self, ex):
        x, y = ex["x"], ex["y"] + HUD_HEIGHT
        r = ex["radius"]
        for i, color in enumerate(["#fff59d", "#ffb74d", "#ef5350"]):
            rr = max(2, r - i * 2)
            self.canvas.create_oval(x - rr, y - rr, x + rr, y + rr, outline=color, width=2)

    def draw_overlay(self):
        if self.paused and not self.game_over:
            self.canvas.create_rectangle(0, HUD_HEIGHT, WIDTH, HEIGHT, fill="#000000", stipple="gray50")
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text="暂停中", fill="white", font=self.big_font)
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 36, text="按 P 继续", fill=COLORS["hud_muted"], font=self.title_font)
            return

        if self.game_over:
            self.canvas.create_rectangle(0, HUD_HEIGHT, WIDTH, HEIGHT, fill="#000000", stipple="gray50")
            self.canvas.create_rectangle(WIDTH // 2 - 220, HEIGHT // 2 - 95, WIDTH // 2 + 220, HEIGHT // 2 + 110, fill="#0f172a", outline=COLORS["hud_accent"], width=2)
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2 - 50, text="GAME OVER", fill="#ef4444", font=self.big_font)
            self.canvas.create_text(
                WIDTH // 2,
                HEIGHT // 2,
                text=f"最终得分 {self.score:05d}   ·   迎击波次 第 {self.wave} 波",
                fill="white",
                font=self.title_font,
            )
            self.canvas.create_text(
                WIDTH // 2,
                HEIGHT // 2 + 32,
                text="按 R 键 或 点击下方按钮重新出发",
                fill=COLORS["hud_muted"],
                font=self.title_font,
            )
            self.show_restart_button()

    def render(self):
        self.canvas.delete("all")
        self.draw_background()
        self.draw_hud()

        for w in self.walls:
            self.draw_wall(w)

        self.draw_base()
        self.draw_tank(self.player, is_player=True)

        for e in self.enemies:
            self.draw_tank(e)

        for b in self.bullets:
            self.draw_bullet(b)

        for p in self.powerups:
            self.draw_powerup(p)

        for ex in self.explosions:
            self.draw_explosion(ex)

        self.draw_overlay()

        if not self.game_over:
            self.hide_restart_button()


# 移动端适配注入
def patch_mobile_hud():
    if is_mobile_env():
        old_draw_hud = TankGame.draw_hud
        def new_draw_hud(self):
            old_draw_hud(self)
            self.canvas.create_rectangle(
                WIDTH // 2 - 110, HUD_HEIGHT - 39,
                WIDTH // 2 + 110, HUD_HEIGHT - 7,
                fill="#1e293b", outline="#38bdf8", width=1
            )
            self.canvas.create_text(
                WIDTH // 2, HUD_HEIGHT - 22,
                text="滑动或使用屏幕摇杆移动与射击",
                fill="#38bdf8",
                font=self.small_font,
                anchor="c"
            )
        TankGame.draw_hud = new_draw_hud

patch_mobile_hud()


if __name__ == "__main__":
    TankGame()