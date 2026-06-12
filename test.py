import tkinter as tk
import random

# --- 游戏参数配置 ---
WIDTH = 600          # 游戏窗口宽度
HEIGHT = 400         # 游戏窗口高度
SPACE_SIZE = 20      # 蛇身和食物的方块大小（像素）
SPEED = 150          # 游戏速度（毫秒/帧，数字越小越快）
BODY_COLOR = "#00FF00" # 蛇身颜色（绿色）
HEAD_COLOR = "#00AA00" # 蛇头颜色（深绿）
FOOD_COLOR = "#FF0000" # 食物颜色（红色）
BG_COLOR = "#000000"   # 背景颜色（黑色）

class SnakeGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("经典贪吃蛇")
        self.window.resizable(False, False)

        self.score = 0
        self.direction = "down"

        # 分数标签
        self.label = tk.Label(self.window, text="分数: {}".format(self.score), font=("Consolas", 20))
        self.label.pack()

        # 游戏画布
        self.canvas = tk.Canvas(self.window, bg=BG_COLOR, height=HEIGHT, width=WIDTH)
        self.canvas.pack()

        # 绑定键盘方向键
        self.window.bind('<Left>', lambda event: self.change_direction('left'))
        self.window.bind('<Right>', lambda event: self.change_direction('right'))
        self.window.bind('<Up>', lambda event: self.change_direction('up'))
        self.window.bind('<Down>', lambda event: self.change_direction('down'))

        # 初始化蛇和食物
        self.snake_coordinates = [[100, 100], [100, 80], [100, 60]] # 初始三节身体
        self.snake_squares = []
        self.food_coordinates = []

        self.create_snake()
        self.create_food()
        self.next_turn()

        self.window.mainloop()

    def create_snake(self):
        """绘制初始的蛇"""
        for i, (x, y) in enumerate(self.snake_coordinates):
            color = HEAD_COLOR if i == 0 else BODY_COLOR
            square = self.canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=color, tag="snake")
            self.snake_squares.append(square)

    def create_food(self):
        """在地图上随机生成食物"""
        while True:
            x = random.randint(0, int((WIDTH / SPACE_SIZE)) - 1) * SPACE_SIZE
            y = random.randint(0, int((HEIGHT / SPACE_SIZE)) - 1) * SPACE_SIZE
            self.food_coordinates = [x, y]
            
            # 确保食物不会生成在蛇的身体上
            if self.food_coordinates not in self.snake_coordinates:
                break

        self.canvas.create_oval(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=FOOD_COLOR, tag="food")

    def next_turn(self):
        """游戏的主循环逻辑（每一帧走一步）"""
        x, y = self.snake_coordinates[0]

        # 根据当前方向计算蛇头的新坐标
        if self.direction == "up":
            y -= SPACE_SIZE
        elif self.direction == "down":
            y += SPACE_SIZE
        elif self.direction == "left":
            x -= SPACE_SIZE
        elif self.direction == "right":
            x += SPACE_SIZE

        # 将新蛇头加入坐标列表
        self.snake_coordinates.insert(0, [x, y])
        square = self.canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=HEAD_COLOR)
        self.snake_squares.insert(0, square)
        
        # 将原来的蛇头（第二节）颜色改回普通身体颜色
        if len(self.snake_squares) > 1:
            self.canvas.itemconfig(self.snake_squares[1], fill=BODY_COLOR)

        # 检查是否吃到食物
        if x == self.food_coordinates[0] and y == self.food_coordinates[1]:
            self.score += 1
            self.label.config(text="分数: {}".format(self.score))
            self.canvas.delete("food")
            self.create_food()
        else:
            # 如果没吃到食物，删掉蛇尾（保持长度不变）
            del self.snake_coordinates[-1]
            self.canvas.delete(self.snake_squares[-1])
            del self.snake_squares[-1]

        # 检查是否碰撞（游戏结束）
        if self.check_collisions():
            self.game_over()
        else:
            # 循环调用自身，继续下一帧
            self.window.after(SPEED, self.next_turn)

    def change_direction(self, new_direction):
        """改变蛇的移动方向，防止直接180度回头"""
        if new_direction == 'left' and self.direction != 'right':
            self.direction = new_direction
        elif new_direction == 'right' and self.direction != 'left':
            self.direction = new_direction
        elif new_direction == 'up' and self.direction != 'down':
            self.direction = new_direction
        elif new_direction == 'down' and self.direction != 'up':
            self.direction = new_direction

    def check_collisions(self):
        """碰撞检测：撞墙或撞到自己"""
        x, y = self.snake_coordinates[0]

        # 撞墙检测
        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            return True

        # 撞自己检测
        if [x, y] in self.snake_coordinates[1:]:
            return True

        return False

    def game_over(self):
        """游戏结束显示"""
        self.canvas.delete("all")
        self.canvas.create_text(
            self.canvas.winfo_width()/2, 
            self.canvas.winfo_height()/2,
            font=('Consolas', 40), 
            text="GAME OVER", 
            fill="red", 
            tag="gameover"
        )

# 启动游戏
if __name__ == "__main__":
    SnakeGame()


    