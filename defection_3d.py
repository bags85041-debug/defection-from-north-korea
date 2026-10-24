from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math

app = Ursina(title="탈북 - 3D 탈출 게임", fullscreen=False)
camera.position = (0, 2, -20)

# 게임 상태
game_over = False
victory = False
health = 3
inventory = {"gun": 0, "axe": 0, "food": 0}
message_text = ""
message_time = 0

# 텍스트 표시용
info_text = Text(text="", position=(-0.85, 0.45), scale=1.5)
inventory_text = Text(text="", position=(-0.85, 0.35), scale=1.2)
message_display = Text(text="", position=(0, -0.45), scale=2, color=color.yellow)
rules_text = Text(text="", position=(0, 0.35), scale=1.1, color=color.cyan)

# 맵 생성
ground = Entity(model='cube', scale=(100, 0.5, 100), position=(0, -1, 50), color=color.gray, collider='box')

# 북쪽 끝 (승리 지점) - 파란색 큰 큐브
victory_zone = Entity(model='cube', scale=(80, 3, 5), position=(0, 1, 100), color=color.blue, collider='box', opacity=0.5)

# 남쪽 시작 지점 - 초록색
start_zone = Entity(model='cube', scale=(80, 3, 5), position=(0, 1, 0), color=color.green, collider='box', opacity=0.5)

# 플레이어 (1인칭 컨트롤러)
player = FirstPersonController()
player.position = (0, 1, 0)
player.speed = 10
player.mouse_sensitivity = Vec3(80, 80, 0)

# 인간 형태의 엔티티 생성 함수
def create_human(position, color_value, is_player=False):
    """인간 형태의 3D 객체 생성 (머리, 몸통, 팔, 다리)"""
    human = Entity()
    human.position = position

    if is_player:
        return human

    # 머리
    head = Entity(model='sphere', scale=0.4, position=(0, 1.6, 0), color=color.orange, parent=human)

    # 몸통
    body = Entity(model='cube', scale=(0.35, 0.8, 0.25), position=(0, 0.9, 0), color=color_value, parent=human)

    # 왼쪽 팔
    left_arm = Entity(model='cube', scale=(0.15, 0.7, 0.15), position=(-0.35, 0.8, 0), color=color.orange, parent=human)

    # 오른쪽 팔
    right_arm = Entity(model='cube', scale=(0.15, 0.7, 0.15), position=(0.35, 0.8, 0), color=color.orange, parent=human)

    # 왼쪽 다리
    left_leg = Entity(model='cube', scale=(0.15, 0.8, 0.15), position=(-0.15, 0.2, 0), color=color.dark_gray, parent=human)

    # 오른쪽 다리
    right_leg = Entity(model='cube', scale=(0.15, 0.8, 0.15), position=(0.15, 0.2, 0), color=color.dark_gray, parent=human)

    return human

# 아이템 클래스
class Item(Entity):
    def __init__(self, position, item_type):
        self.item_type = item_type
        colors = {"gun": color.red, "axe": color.brown, "food": color.yellow}
        names_kr = {"gun": "총", "axe": "도끼", "food": "식량"}

        super().__init__(
            model='cube',
            scale=0.5,
            position=position,
            color=colors[item_type],
            collider='box'
        )
        self.info_text = Text(text=names_kr[item_type], position=(position[0], position[1] + 0.5, position[2]), scale=1, background=True)

    def pickup(self):
        global message_text, message_time
        inventory[self.item_type] += 1
        names_kr = {"gun": "총", "axe": "도끼", "food": "식량"}
        message_text = f"✓ {names_kr[self.item_type]}을(를) 수집했습니다!"
        message_time = 120
        self.info_text.text = ""
        destroy(self)

# 군인 NPC 클래스
class Soldier:
    def __init__(self, position):
        self.start_pos = position
        self.human = create_human(position, color.red)
        self.speed = 5
        self.patrol_distance = 30
        self.direction = random.choice([-1, 1])
        self.start_x = position[0]
        self.pos_x = position[0]
        self.pos_y = position[1]
        self.pos_z = position[2]

        # 군인 표시 (빨간 경고)
        self.indicator = Text(text="⚠️ 군인", position=(position[0], position[1] + 2.2, position[2]), scale=2, color=color.red)

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

# 게임 규칙 표시
rules = """
⚔️ 탈북 3D 게임 규칙 ⚔️
🎯 목표: 파란 지점(북쪽)에 도달하여 탈출하기
🔴 빨간 군인들을 피하세요 (접촉 시 체력 감소)
📦 아이템 수집: 총(빨강), 도끼(갈색), 식량(노랑)
❤️ 식량으로 체력 회복 (R키)
💀 체력이 0이 되면 게임 오버
"""

# 키보드 입력
def input(key):
    global message_text, message_time, health, victory, game_over, inventory

    if key == 'e':  # 아이템 수집
        for item in items:
            dist = distance(player.position, item.position)
            if dist < 3:
                item.pickup()
                items.remove(item)
                break

    if key == 'r':  # 식량 섭취
        if inventory["food"] > 0:
            inventory["food"] -= 1
            health = min(health + 1, 5)
            message_text = "🍖 식량을 먹었습니다! +1 체력"
            message_time = 120
        else:
            message_text = "❌ 식량이 없습니다!"
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
    health_bar = "❤" * health + "🖤" * (5 - max(0, health))
    info_text.text = f"체력: {health_bar} | 위치: {player.position.y:.1f}"
    inventory_text.text = f"📦 총: {inventory['gun']} | 도끼: {inventory['axe']} | 식량: {inventory['food']}"

    # 규칙을 계속 표시
    rules_text.text = rules

    # 군인 업데이트
    for soldier in soldiers:
        soldier.update()

        # 군인과 충돌 감지
        dist = soldier.distance_to(player.position.x, player.position.y, player.position.z)
        if dist < 2 and not game_over and not victory:
            health -= 1
            message_text = f"⚠️ 군인에게 발각됨! 체력: {health}/5"
            message_time = 180

            if health <= 0:
                game_over = True
                message_display.text = "❌ GAME OVER\n탈출 실패했습니다..."
                message_display.color = color.red
                message_display.scale = 3
                rules_text.text = ""
            else:
                # 플레이어를 뒤로 밀어냄
                direction = (player.position - soldier.human.position).normalized()
                player.position += direction * 5

    # 승리 조건 체크
    if distance(player.position, victory_zone.position) < 15 and not game_over and not victory:
        victory = True
        message_display.text = "🎉 대한민국에 오신 것을\n환영합니다! 🎉\n탈출 성공!"
        message_display.color = color.gold
        message_display.scale = 3
        rules_text.text = ""

def distance(pos1, pos2):
    return math.sqrt((pos1.x - pos2.x)**2 + (pos1.y - pos2.y)**2 + (pos1.z - pos2.z)**2)

# 스카이박스 (하늘)
sky = Entity(model='cube', scale=500, texture='white_cube', position=(0, 0, 0), double_sided=True, color=color.cyan)

# 조명
directional_light = DirectionalLight(shadow_resolution=(2048, 2048))
directional_light.direction = (-1, -1, 1)

# 안내 텍스트
help_text = Text(
    text="[조작] WASD: 이동 | 마우스: 회전 | E: 수집 | R: 섭취 | ESC: 종료",
    position=(0, -0.47),
    scale=1.1,
    color=color.light_gray
)

# 게임 루프 실행
run()
