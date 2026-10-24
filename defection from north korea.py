import turtle
import random
import math
import time

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
ITEM_GUN = "gun"
ITEM_AXE = "axe"
ITEM_FOOD = "food"

ITEM_NAMES = {
    ITEM_GUN: "총",
    ITEM_AXE: "도끼",
    ITEM_FOOD: "식량"
}

ITEM_COLORS = {
    ITEM_GUN: "red",
    ITEM_AXE: "brown",
    ITEM_FOOD: "yellow"
}

class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.item_type = item_type
        self.turtle = turtle.Turtle()
        self.turtle.speed(0)
        self.turtle.shape("circle")
        self.turtle.color(ITEM_COLORS[item_type])
        self.turtle.penup()
        self.turtle.shapesize(0.7, 0.7)
        self.draw()

    def distance_to(self, x, y):
        return math.sqrt((self.x - x)**2 + (self.y - y)**2)

    def draw(self):
        self.turtle.goto(self.x, self.y)

    def hide(self):
        self.turtle.hideturtle()

class Soldier:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.turtle = turtle.Turtle()
        self.turtle.speed(0)
        self.turtle.shape("triangle")
        self.turtle.color("darkred")
        self.turtle.penup()
        self.turtle.shapesize(1.2, 1.2)
        self.direction = random.choice([-1, 1])
        self.speed = 3
        self.patrol_range = 150
        self.start_x = x
        self.draw()

    def update(self):
        self.x += self.speed * self.direction
        if abs(self.x - self.start_x) > self.patrol_range:
            self.direction *= -1
        self.draw()

    def distance_to(self, x, y):
        return math.sqrt((self.x - x)**2 + (self.y - y)**2)

    def draw(self):
        self.turtle.goto(self.x, self.y)

    def hide(self):
        self.turtle.hideturtle()

class Player:
    def __init__(self, name, start_x=0, start_y=0):
        self.name = name
        self.x = start_x
        self.y = start_y
        self.speed = 8
        self.health = 3
        self.inventory = [None] * 9

        self.turtle = turtle.Turtle()
        self.turtle.speed(0)
        self.turtle.shape("square")
        self.turtle.color("lime")
        self.turtle.penup()
        self.turtle.shapesize(1, 1)
        self.draw()

    def setup_keys(self):
        screen.onkey(self.move_up, "w")
        screen.onkey(self.move_down, "s")
        screen.onkey(self.move_left, "a")
        screen.onkey(self.move_right, "d")
        screen.onkey(self.pickup_item, "e")
        screen.onkey(self.eat_food, "r")

    def move_up(self):
        self.y = min(self.y + self.speed, WINDOW_HEIGHT // 2 - 30)
        self.draw()

    def move_down(self):
        self.y = max(self.y - self.speed, -WINDOW_HEIGHT // 2 + 30)
        self.draw()

    def move_left(self):
        self.x = max(self.x - self.speed, -WINDOW_WIDTH // 2 + 30)
        self.draw()

    def move_right(self):
        self.x = min(self.x + self.speed, WINDOW_WIDTH // 2 - 30)
        self.draw()

    def draw(self):
        self.turtle.goto(self.x, self.y)

    def add_item(self, item_type):
        for i in range(len(self.inventory)):
            if self.inventory[i] is None:
                self.inventory[i] = item_type
                return True
        return False

    def get_inventory_count(self):
        return sum(1 for item in self.inventory if item is not None)

    def take_damage(self):
        self.health -= 1

    def pickup_item(self):
        global game_state
        for item in items[:]:
            if item.distance_to(self.x, self.y) < 40:
                if self.add_item(item.item_type):
                    show_message(f"{ITEM_NAMES[item.item_type]}을(를) 수집했습니다! (E키로 다시 사용)")
                    item.hide()
                    items.remove(item)
                else:
                    show_message("인벤토리가 가득 찼습니다!")
                return

    def eat_food(self):
        for i in range(len(self.inventory)):
            if self.inventory[i] == ITEM_FOOD:
                self.inventory[i] = None
                show_message("식량을 먹었습니다! +1체력")
                self.health = min(self.health + 1, 5)
                update_inventory_display()
                return
        show_message("식량이 없습니다!")

def create_items():
    items_data = [
        (250, 200, ITEM_GUN),
        (-250, 200, ITEM_AXE),
        (-300, 0, ITEM_FOOD),
        (200, -150, ITEM_FOOD),
        (-100, 150, ITEM_GUN),
        (100, 250, ITEM_FOOD),
        (350, -100, ITEM_FOOD),
        (-350, -150, ITEM_AXE),
    ]
    return [Item(x, y, item_type) for x, y, item_type in items_data]

def create_soldiers():
    soldiers_data = [
        (-200, 200),
        (200, -100),
        (0, 250),
    ]
    return [Soldier(x, y) for x, y in soldiers_data]

def draw_ui():
    ui_display.clear()
    ui_display.goto(-WINDOW_WIDTH // 2 + 20, WINDOW_HEIGHT // 2 - 20)

    health_bar = "❤" * player.health + "🖤" * (5 - max(0, player.health))
    ui_text = f"[{player.name}] 체력: {health_bar}  인벤토리: {player.get_inventory_count()}/9"
    ui_display.write(ui_text, font=("Arial", 13, "bold"))

def update_inventory_display():
    inventory_display.clear()
    y_offset = WINDOW_HEIGHT // 2 - 50
    inventory_display.goto(-WINDOW_WIDTH // 2 + 20, y_offset)
    inventory_display.write("📦 인벤토리:", font=("Arial", 11, "bold"))

    for i in range(9):
        x = -WINDOW_WIDTH // 2 + 30 + (i % 9) * 55
        y = y_offset - 25 - (i // 9) * 28

        inventory_display.goto(x, y)
        inventory_display.color("white")

        if player.inventory[i]:
            item_name = ITEM_NAMES[player.inventory[i]][0]
            color = ITEM_COLORS[player.inventory[i]]
            inventory_display.color(color)
            inventory_display.write(f"{i+1}:{item_name}", font=("Arial", 9, "normal"))
        else:
            inventory_display.color("gray")
            inventory_display.write(f"{i+1}:_", font=("Arial", 9, "normal"))

def show_message(text):
    global message_time
    message_display.clear()
    message_display.goto(0, -WINDOW_HEIGHT // 2 + 25)
    message_display.write(text, align="center", font=("Arial", 11, "normal"))
    message_time = 120

def check_soldier_collision():
    for soldier in soldiers:
        dist = soldier.distance_to(player.x, player.y)
        if dist < 35:
            return True
    return False

def draw_rules():
    rules_display.clear()
    rules_display.goto(-WINDOW_WIDTH // 2 + 15, WINDOW_HEIGHT // 2 - 100)

    rules = [
        "⚔️ 게임 규칙 ⚔️",
        "1. 숲에서 도망치세요! (위쪽 끝에 도달하면 승리)",
        "2. 총, 도끼, 식량을 수집하세요 (E키)",
        "3. 빨간 삼각형(군인)을 피하세요!",
        "4. 군인과 접촉하면 체력이 감소합니다",
        "5. 식량(R키)으로 체력을 회복하세요",
        "6. 체력이 0이 되면 게임 오버입니다"
    ]

    for i, rule in enumerate(rules):
        rules_display.goto(-WINDOW_WIDTH // 2 + 15, WINDOW_HEIGHT // 2 - 100 - i * 25)
        if i == 0:
            rules_display.color("yellow")
            rules_display.write(rule, font=("Arial", 13, "bold"))
        else:
            rules_display.color("white")
            rules_display.write(rule, font=("Arial", 10, "normal"))

screen = turtle.Screen()
screen.setup(WINDOW_WIDTH, WINDOW_HEIGHT)
screen.bgcolor("darkgreen")
screen.title("탈북 - Defection from North Korea")

# Game state
game_state = "setup"  # setup, playing, game_over, victory
message_time = 0

player = Player("", 0, 0)
items = create_items()
soldiers = create_soldiers()

# Turtles for UI
ui_display = turtle.Turtle()
ui_display.speed(0)
ui_display.hideturtle()
ui_display.color("white")
ui_display.penup()

inventory_display = turtle.Turtle()
inventory_display.speed(0)
inventory_display.hideturtle()
inventory_display.color("white")
inventory_display.penup()

message_display = turtle.Turtle()
message_display.speed(0)
message_display.hideturtle()
message_display.color("yellow")
message_display.penup()

rules_display = turtle.Turtle()
rules_display.speed(0)
rules_display.hideturtle()
rules_display.penup()

controls_display = turtle.Turtle()
controls_display.speed(0)
controls_display.hideturtle()
controls_display.color("lightgray")
controls_display.penup()
controls_display.goto(WINDOW_WIDTH // 2 - 350, -WINDOW_HEIGHT // 2 + 25)
controls_display.write("🎮 WASD: 이동  E: 수집  R: 먹기", font=("Arial", 11, "bold"))

# Draw rules first
draw_rules()
show_message("게임을 시작하려면 이름을 입력하고 엔터를 누르세요!")

name_input = turtle.textinput("탈북 게임", "탈북자의 이름을 입력하세요:")
if name_input and name_input.strip():
    player.name = name_input
    game_state = "playing"
    player.setup_keys()
    show_message(f"시작! {player.name}님, 위쪽으로 탈출하세요! 군인(빨강)을 피하세요!")
    rules_display.clear()

draw_ui()
update_inventory_display()

# Game loop
frame = 0
while game_state in ["playing", "setup"] or (game_state == "game_over" and frame < 300):
    frame += 1

    if game_state == "playing":
        # Update soldiers
        for soldier in soldiers:
            soldier.update()

        # Check soldier collision
        if frame % 10 == 0 and check_soldier_collision():
            player.take_damage()
            show_message(f"⚠️ 군인에게 발각되었습니다! 체력: {player.health}/5")
            if player.health <= 0:
                game_state = "game_over"
                message_display.clear()
                message_display.goto(0, 0)
                message_display.color("red")
                message_display.write("❌ 게임 오버!\n탈출 실패...", align="center", font=("Arial", 24, "bold"))
                rules_display.clear()
                rules_display.goto(0, -50)
                rules_display.color("white")
                rules_display.write("(3초 후 종료됩니다)", align="center", font=("Arial", 12, "normal"))

        # Check victory condition
        if player.y >= WINDOW_HEIGHT // 2 - 40:
            game_state = "victory"
            message_display.clear()
            message_display.goto(0, 0)
            message_display.color("gold")
            message_display.write("🎉 대한민국에 오신 것을 환영합니다! 🎉", align="center", font=("Arial", 20, "bold"))
            rules_display.clear()
            rules_display.goto(0, -80)
            rules_display.color("lightgreen")
            rules_display.write(f"축하합니다, {player.name}님! 탈출 성공!", align="center", font=("Arial", 14, "normal"))

        draw_ui()
        update_inventory_display()

    screen.update()
    time.sleep(0.05)

screen.mainloop()
