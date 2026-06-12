import tkinter as tk
import random

WIDTH = 800
HEIGHT = 600
TANK_SIZE = 30
BULLET_SIZE = 6
BLOCK_SIZE = 40
FPS = 30            

class TankGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("坦克大战")
        self.window.resizable(False, False)

        self.game_over_status = False
        self.score = 0

        self.label = tk.Label(self.window, text="得分: 0  |  控制: WASD移动，Space开火", font=("Arial", 14))
        self.label.pack()

        self.canvas = tk.Canvas(self.window, bg="black", width=WIDTH, height=HEIGHT)
        self.canvas.pack()

        self.keys = {'w': False, 's': False, 'a': False, 'd': False, 'space': False}
        self.bullet_cooldown = 0 

        self.window.bind("<KeyPress>", self.press)
        self.window.bind("<KeyRelease>", self.release)

        self.player = {"x": WIDTH//2, "y": HEIGHT - 60, "dir": "U", "speed": 5, "color": "yellow"}
        self.enemies = []
        self.bullets = []   
        self.walls = []     

        self.init_map()
        self.spawn_enemy(3) 
        
        self.game_loop()
        self.window.mainloop()

    def init_map(self):
        """随机生成一些砖墙"""
        for _ in range(15):
            wx = random.randint(2, (WIDTH//BLOCK_SIZE)-3) * BLOCK_SIZE
            wy = random.randint(2, (HEIGHT//BLOCK_SIZE)-5) * BLOCK_SIZE
            if wy < HEIGHT - 120: 
                self.walls.append({"x": wx, "y": wy, "hp": 2})

    def spawn_enemy(self, count=1):
        """在顶部随机生成敌人"""
        for _ in range(count):
            ex = random.randint(1, (WIDTH//BLOCK_SIZE)-2) * BLOCK_SIZE
            ey = 40
            self.enemies.append({"x": ex, "y": ey, "dir": "D", "speed": 3, "color": "red", "cooldown": 0})

    def press(self, event):
        key = event.keysym.lower()
        if key in ['w', 'up']: self.keys['w'] = True
        elif key in ['s', 'down']: self.keys['s'] = True
        elif key in ['a', 'left']: self.keys['a'] = True
        elif key in ['d', 'right']: self.keys['d'] = True
        if event.keysym == "space": self.keys['space'] = True

    def release(self, event):
        key = event.keysym.lower()
        if key in ['w', 'up']: self.keys['w'] = False
        elif key in ['s', 'down']: self.keys['s'] = False
        elif key in ['a', 'left']: self.keys['a'] = False
        elif key in ['d', 'right']: self.keys['d'] = False
        if event.keysym == "space": self.keys['space'] = False

    def game_loop(self):
        if self.game_over_status:
            return

        self.update_player()
        self.update_enemies()
        self.update_bullets()
        self.check_collisions()
        
        self.render()

        if len(self.enemies) < 3 and random.random() < 0.02:
            self.spawn_enemy(1)

        self.window.after(1000 // FPS, self.game_loop)

    def check_wall_collision(self, next_x, next_y):
        """检查给定的坐标是否会撞墙"""
        temp_tank = {"x": next_x, "y": next_y}
        for w in self.walls:
            if self.is_collide(temp_tank, TANK_SIZE, w, BLOCK_SIZE):
                return True
        return False

    def update_player(self):
        next_x, next_y = self.player['x'], self.player['y']
        moved = False

        if self.keys['w']:
            next_y -= self.player['speed']
            self.player['dir'] = "U"
            moved = True
        elif self.keys['s']:
            next_y += self.player['speed']
            self.player['dir'] = "D"
            moved = True
        
        if not moved: 
            if self.keys['a']:
                next_x -= self.player['speed']
                self.player['dir'] = "L"
            elif self.keys['d']:
                next_x += self.player['speed']
                self.player['dir'] = "R"

        if 0 <= next_x <= WIDTH - TANK_SIZE and 0 <= next_y <= HEIGHT - TANK_SIZE:
            if not self.check_wall_collision(next_x, next_y):
                self.player['x'], self.player['y'] = next_x, next_y

        if self.bullet_cooldown > 0:
            self.bullet_cooldown -= 1
        if self.keys['space'] and self.bullet_cooldown == 0:
            self.shoot(self.player, "player")
            self.bullet_cooldown = 8 

    def update_enemies(self):
        for e in self.enemies:
            if random.random() < 0.04:
                e['dir'] = random.choice(["U", "D", "L", "R"])
            
            next_x, next_y = e['x'], e['y']
            if e['dir'] == "U": next_y -= e['speed']
            elif e['dir'] == "D": next_y += e['speed']
            elif e['dir'] == "L": next_x -= e['speed']
            elif e['dir'] == "R": next_x += e['speed']

            if 0 <= next_x <= WIDTH - TANK_SIZE and 0 <= next_y <= HEIGHT - TANK_SIZE and not self.check_wall_collision(next_x, next_y):
                e['x'], e['y'] = next_x, next_y
            else:
                e['dir'] = random.choice(["U", "D", "L", "R"])

            if e['cooldown'] > 0:
                e['cooldown'] -= 1
            elif random.random() < 0.03:
                self.shoot(e, "enemy")
                e['cooldown'] = 30

    def shoot(self, tank, t_type):
        bx, by = tank['x'] + TANK_SIZE//2, tank['y'] + TANK_SIZE//2
        self.bullets.append({"x": bx, "y": by, "dir": tank['dir'], "type": t_type, "speed": 10})

    def update_bullets(self):
        for b in self.bullets[:]:
            if b['dir'] == "U": b['y'] -= b['speed']
            elif b['dir'] == "D": b['y'] += b['speed']
            elif b['dir'] == "L": b['x'] -= b['speed']
            elif b['dir'] == "R": b['x'] += b['speed']
            
            if b['x'] < 0 or b['x'] > WIDTH or b['y'] < 0 or b['y'] > HEIGHT:
                if b in self.bullets: self.bullets.remove(b)

    def is_collide(self, obj1, size1, obj2, size2):
        return (obj1['x'] < obj2['x'] + size2 and
                obj1['x'] + size1 > obj2['x'] and
                obj1['y'] < obj2['y'] + size2 and
                obj1['y'] + size1 > obj2['y'])

    def check_collisions(self):
        for b in self.bullets[:]:
            bullet_removed = False
            
            for w in self.walls[:]:
                if self.is_collide(b, BULLET_SIZE, w, BLOCK_SIZE):
                    w['hp'] -= 1
                    if w['hp'] <= 0: 
                        self.walls.remove(w)
                    if b in self.bullets: 
                        self.bullets.remove(b)
                    bullet_removed = True
                    break
            if bullet_removed: continue

            if b['type'] == "player":
                for e in self.enemies[:]:
                    if self.is_collide(b, BULLET_SIZE, e, TANK_SIZE):
                        self.enemies.remove(e)
                        if b in self.bullets: self.bullets.remove(b)
                        self.score += 100
                        self.label.config(text=f"得分: {self.score}  |  控制: WASD或方向键移动，Space开火")
                        bullet_removed = True
                        break
            elif b['type'] == "enemy":
                if self.is_collide(b, BULLET_SIZE, self.player, TANK_SIZE):
                    self.game_over_status = True

    def draw_tank(self, tank):
        x, y, d = tank['x'], tank['y'], tank['dir']
        self.canvas.create_rectangle(x, y, x+TANK_SIZE, y+TANK_SIZE, fill=tank['color'], outline="white")
        if d == "U": self.canvas.create_line(x+TANK_SIZE//2, y, x+TANK_SIZE//2, y-10, fill="white", width=4)
        elif d == "D": self.canvas.create_line(x+TANK_SIZE//2, y+TANK_SIZE, x+TANK_SIZE//2, y+TANK_SIZE+10, fill="white", width=4)
        elif d == "L": self.canvas.create_line(x, y+TANK_SIZE//2, x-10, y+TANK_SIZE//2, fill="white", width=4)
        elif d == "R": self.canvas.create_line(x+TANK_SIZE, y+TANK_SIZE//2, x+TANK_SIZE+10, y+TANK_SIZE//2, fill="white", width=4)

    def render(self):
        self.canvas.delete("all")

        for w in self.walls:
            color = "#8B4513" if w['hp'] == 2 else "#CD853F"
            self.canvas.create_rectangle(w['x'], w['y'], w['x']+BLOCK_SIZE, w['y']+BLOCK_SIZE, fill=color, outline="black")

        self.draw_tank(self.player)

        for e in self.enemies:
            self.draw_tank(e)

        for b in self.bullets:
            color = "white" if b['type'] == "player" else "orange"
            self.canvas.create_oval(b['x']-BULLET_SIZE//2, b['y']-BULLET_SIZE//2, 
                                    b['x']+BULLET_SIZE//2, b['y']+BULLET_SIZE//2, fill=color)

        if self.game_over_status:
            self.canvas.create_text(WIDTH//2, HEIGHT//2, text="GAME OVER", fill="red", font=("Arial", 40, "bold"))

if __name__ == "__main__":
    TankGame()