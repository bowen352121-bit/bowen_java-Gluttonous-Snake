import tkinter as tk
import random

WIDTH = 600
HEIGHT = 400
CELL_SIZE = 20
SPEED = 150
BG_COLOR = "#000000"
HEAD_COLOR = "#00AA00"
BODY_COLOR = "#00FF00"
FOOD_COLOR = "#FF0000"


class SnakeGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("经典贪吃蛇")
        self.window.resizable(False, False)

        self.score = 0
        self.direction = "down"
        self.game_over = False

        self.label = tk.Label(
            self.window,
            text="分数: 0  |  控制: 方向键 / WASD，R 重新开始",
            font=("Arial", 14),
        )
        self.label.pack()

        self.canvas = tk.Canvas(self.window, bg=BG_COLOR, width=WIDTH, height=HEIGHT)
        self.canvas.pack()

        self.window.bind("<KeyPress>", self.on_key_press)

        self.snake = [[100, 100], [100, 80], [100, 60]]
        self.snake_items = []
        self.food = None
        self.food_item = None

        self.reset_game()
        self.window.mainloop()

    def reset_game(self):
        self.game_over = False
        self.score = 0
        self.direction = "down"
        self.snake = [[100, 100], [100, 80], [100, 60]]
        self.label.config(text="分数: 0  |  控制: 方向键 / WASD，R 重新开始")

        self.canvas.delete("all")
        self.snake_items = []
        self.food_item = None

        self.draw_snake()
        self.spawn_food()
        self.tick()

    def draw_snake(self):
        self.snake_items = []
        for i, (x, y) in enumerate(self.snake):
            color = HEAD_COLOR if i == 0 else BODY_COLOR
            item = self.canvas.create_rectangle(
                x, y, x + CELL_SIZE, y + CELL_SIZE, fill=color, tag="snake"
            )
            self.snake_items.append(item)

    def spawn_food(self):
        cols = WIDTH // CELL_SIZE
        rows = HEIGHT // CELL_SIZE
        while True:
            x = random.randint(0, cols - 1) * CELL_SIZE
            y = random.randint(0, rows - 1) * CELL_SIZE
            if [x, y] not in self.snake:
                self.food = [x, y]
                break

        if self.food_item:
            self.canvas.delete(self.food_item)

        x, y = self.food
        self.food_item = self.canvas.create_oval(
            x, y, x + CELL_SIZE, y + CELL_SIZE, fill=FOOD_COLOR, tag="food"
        )

    def tick(self):
        if self.game_over:
            return

        head_x, head_y = self.snake[0]
        if self.direction == "up":
            head_y -= CELL_SIZE
        elif self.direction == "down":
            head_y += CELL_SIZE
        elif self.direction == "left":
            head_x -= CELL_SIZE
        elif self.direction == "right":
            head_x += CELL_SIZE

        new_head = [head_x, head_y]
        self.snake.insert(0, new_head)

        head_item = self.canvas.create_rectangle(
            head_x,
            head_y,
            head_x + CELL_SIZE,
            head_y + CELL_SIZE,
            fill=HEAD_COLOR,
            tag="snake",
        )
        self.snake_items.insert(0, head_item)

        if len(self.snake_items) > 1:
            self.canvas.itemconfig(self.snake_items[1], fill=BODY_COLOR)

        if new_head == self.food:
            self.score += 1
            self.label.config(
                text=f"分数: {self.score}  |  控制: 方向键 / WASD，R 重新开始"
            )
            self.spawn_food()
        else:
            self.snake.pop()
            self.canvas.delete(self.snake_items.pop())

        if self.is_collision(new_head):
            self.end_game()
        else:
            self.window.after(SPEED, self.tick)

    def is_collision(self, head):
        x, y = head
        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            return True
        return head in self.snake[1:]

    def end_game(self):
        self.game_over = True
        self.canvas.create_text(
            WIDTH // 2,
            HEIGHT // 2 - 20,
            font=("Arial", 36),
            text="GAME OVER",
            fill="red",
        )
        self.canvas.create_text(
            WIDTH // 2,
            HEIGHT // 2 + 30,
            font=("Arial", 16),
            text="按 R 重新开始",
            fill="white",
        )

    def change_direction(self, new_direction):
        opposites = {
            "up": "down",
            "down": "up",
            "left": "right",
            "right": "left",
        }
        if new_direction != opposites.get(self.direction):
            self.direction = new_direction

    def on_key_press(self, event):
        key = event.keysym.lower()

        if key in ("r",):
            self.reset_game()
            return

        direction_map = {
            "up": "up",
            "down": "down",
            "left": "left",
            "right": "right",
            "w": "up",
            "s": "down",
            "a": "left",
            "d": "right",
        }
        if key in direction_map:
            self.change_direction(direction_map[key])


if __name__ == "__main__":
    SnakeGame()
