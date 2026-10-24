from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math

app = Ursina(title="[탈북] 3D 탈출 게임", fullscreen=False)
camera.position = (0, 2, -20)

# 게임 상태
game_over = False
victory = False
health = 3
inventory = {"gun": 0, "axe": 0, "food": 0}
message_text = ""
message_time = 0

# 텍스트 표시용 (한글은 이모지로 대체)
info_text = Text(text="", position=(-0.85, 0.45), scale=1.3)
inventory_text = Text(text="", position=(-0.85, 0.35), scale=1.0)
message_display = Text(text="", position=(0, -0.45), scale=1.8, color=(1, 1, 0))  # 노란색
rules_text = Text(text="", position=(0, 0.35), scale=1.0, color=(0, 1, 1))  # 시안색

# 맵 생성
ground = Entity(model='cube', scale=(100, 0.5, 100), position=(0, -1, 50), color=(0.5, 0.5, 0.5, 1))

# 북쪽 끝 (승리 지점) - 파란색
victory_zone = Entity(model='cube', scale=(80, 3, 5), position=(0, 1, 100), color=(0, 0, 1, 0.5))

# 남쪽 시작 지점 - 초록색
start_zone = Entity(model='cube', scale=(80, 3, 5), position=(0, 1, 0), color=(0, 1, 0, 0.5))

# 플레이어 (1인칭 컨트롤러)
player = FirstPersonController()
player.position = (0, 1, 0)
player.speed = 10
player.mouse_sensitivity = Vec3(80, 80, 0)

# 인간 형태의 엔티티 생성 함수
def create_human(position, r, g, b):
    """인간 형태의 3D 객체 생성"""
    human = Entity()
    human.position = position

    # 머리 (주황색)
    head = Entity(model='sphere', scale=0.4, position=(0, 1.6, 0), color=(1, 0.6, 0, 1), parent=human)

    # 몸통
    body = Entity(model='cube', scale=(0.35, 0.8, 0.25), position=(0, 0.9, 0), color=(r, g, b, 1), parent=human)

    # 팔
    left_arm = Entity(model='cube', scale=(0.15, 0.7, 0.15), position=(-0.35, 0.8, 0), color=(1, 0.6, 0, 1), parent=human)
    right_arm = Entity(model='cube', scale=(0.15, 0.7, 0.15), position=(0.35, 0.8, 0), color=(1, 0.6, 0, 1), parent=human)

    # 다리
    left_leg = Entity(model='cube', scale=(0.15, 0.8, 0.15), position=(-0.15, 0.2, 0), color=(0.3, 0.3, 0.3, 1), parent=human)
    right_leg = Entity(model='cube', scale=(0.15, 0.8, 0.15), position=(0.15, 0.2, 0), color=(0.3, 0.3, 0.3, 1), parent=human)

    return human

# 아이템 클래스
class Item(Entity):
    def __init__(self, position, item_type):
        self.item_type = item_type
        colors = {"gun": (1, 0, 0, 1), "axe": (0.6, 0.3, 0, 1), "food": (1, 1, 0, 1)}
        names = {"gun": "[GUN]", "axe": "[AXE]", "food": "[FOOD]"}

        super().__init__(
            model='cube',
            scale=0.5,
            position=position,
            color=colors[item_type],
            collider='box',
            texture=None
        )
        self.item_name = names[item_type]
        self.info_text = Text(text=names[item_type], position=(position[0], position[1] + 0.5, position[2]), scale=0.8, background=True)

    def pickup(self):
        global message_text, message_time
        inventory[self.item_type] += 1
        message_text = f"[GET] {self.item_name}!"
        message_time = 120
        self.info_text.text = ""
        destroy(self)

# 군인 NPC 클래스
class Soldier:
    def __init__(self, position):
        self.human = create_human(position, 1, 0, 0)  # 빨간색 몸통
        self.speed = 5
        self.patrol_distance = 30
        self.direction = random.choice([-1, 1])
        self.start_x = position[0]
        self.pos_x = position[0]
        self.pos_y = position[1]
        self.pos_z = position[2]

        # 군인 표시
        self.indicator = Text(text="[SOLDIER]", position=(position[0], position[1] + 2.2, position[2]), scale=1.5, color=(1, 0, 0))

    def update(self):
        self.pos_x += self.speed * self.direction * 0.016
        if abs(self.pos_x - self.start_x) > self.patrol_distance:
            self.direction *= -1

        self.human.position = (self.pos_x, self.pos_y, self.pos_z)
        self.indicator.position = (self.pos_x, self.pos_y + 2.2, self.pos_z)

    def distance_to(self, x, y, z):
        return math.sqrt((self.pos_x - x)**2 + (self.pos_y - y)**2 + (self.pos_z - z)**2)

# 아이템 생성
items = [
    Item((20, 1, 20), "gun"),
    Item((-20, 1, 20), "axe"),
    Item((0, 1, 30), "food"),
    Item((30, 1, 50), "food"),
    Item((-30, 1, 50), "gun"),
    Item((15, 1, 70), "food"),
    Item((-15, 1, 70), "axe"),
    Item((0, 1, 85), "food"),
]

# 군인 생성
soldiers = [
    Soldier((25, 1, 30)),
    Soldier((-25, 1, 50)),
    Soldier((0, 1, 70)),
]

# 게임 규칙
rules = """
[DEFECTION GAME RULES]
Goal: Reach BLUE zone (North) to ESCAPE
Avoid: RED SOLDIERS - contact = damage
Items: GUN(red) AXE(brown) FOOD(yellow)
Recovery: FOOD restores +1 health
GameOver: Health reaches 0
"""

# 키보드 입력
def input(key):
    global message_text, message_time, health, victory, game_over, inventory

    if key == 'e':  # 아이템 수집
        for item in items[:]:
            dist = distance(player.position, item.position)
            if dist < 3:
                item.pickup()
                items.remove(item)
                break

    if key == 'r':  # 식량 섭취
        if inventory["food"] > 0:
            inventory["food"] -= 1
            health = min(health + 1, 5)
            message_text = "[FOOD] Eaten! +1 Health"
            message_time = 120
        else:
            message_text = "[ERROR] No food!"
            message_time = 120

    if key == 'esc':
        exit()

# 업데이트 함수
def update():
    global message_text, message_time, health, game_over, victory

    # 메시지 시간 감소
    if message_time > 0:
        message_time -= 1
        message_display.text = message_text
    else:
        message_display.text = ""

    # UI 업데이트
    health_str = "H" * health + "-" * (5 - max(0, health))
    info_text.text = f"[HEALTH: {health_str}] POS: {player.position.y:.1f}"
    inventory_text.text = f"[INVENTORY] GUN:{inventory['gun']} AXE:{inventory['axe']} FOOD:{inventory['food']}"

    # 규칙을 계속 표시
    rules_text.text = rules

    # 군인 업데이트
    for soldier in soldiers:
        soldier.update()

        # 군인과 충돌 감지
        dist = soldier.distance_to(player.position.x, player.position.y, player.position.z)
        if dist < 2 and not game_over and not victory:
            health -= 1
            message_text = f"[ALERT] Caught by soldier! Health: {health}/5"
            message_time = 180

            if health <= 0:
                game_over = True
                message_display.text = "[GAME OVER]\nEscape Failed..."
                message_display.color = (1, 0, 0)
                message_display.scale = 2.5
                rules_text.text = ""
            else:
                # 플레이어를 뒤로 밀어냄
                direction = (player.position - soldier.human.position).normalized()
                player.position += direction * 5

    # 승리 조건 체크
    if distance(player.position, victory_zone.position) < 15 and not game_over and not victory:
        victory = True
        message_display.text = "[VICTORY]\nWelcome to South Korea!"
        message_display.color = (1, 1, 0)
        message_display.scale = 2.5
        rules_text.text = ""

def distance(pos1, pos2):
    return math.sqrt((pos1.x - pos2.x)**2 + (pos1.y - pos2.y)**2 + (pos1.z - pos2.z)**2)

# 스카이박스
sky = Entity(model='cube', scale=500, texture='white_cube', position=(0, 0, 0), double_sided=True, color=(0.5, 0.8, 1, 1))

# 조명
directional_light = DirectionalLight(shadow_resolution=(2048, 2048))
directional_light.direction = (-1, -1, 1)

# 안내 텍스트
help_text = Text(
    text="[CONTROLS] WASD:Move Mouse:Look E:Pickup R:Eat ESC:Exit",
    position=(0, -0.48),
    scale=1.0,
    color=(0.7, 0.7, 0.7)
)

# 게임 실행
run()
