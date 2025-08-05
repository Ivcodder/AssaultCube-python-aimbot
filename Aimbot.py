from pymem import Pymem
import math
import time

pm = Pymem("ac_client.exe")
base = pm.base_address

ENTITY_LIST = base + 0x18AC04
LOCAL_PLAYER = base + 0x0017E0A8
PLAYER_COUNT = base + 0x18AC0C

HEAD_X = 0x04
HEAD_Y = 0x08
HEAD_Z = 0x0C
TEAM_NUM = 0x30C
IS_DEAD = 0x318
YAW = 0x34
PITCH = 0x38


def get_player_head_position(player):
    x = pm.read_float(player + HEAD_X)
    y = pm.read_float(player + HEAD_Y)
    z = pm.read_float(player + HEAD_Z)
    return x, y, z

def calculate_angle(src, dst):
    dx = dst[0] - src[0]
    dy = dst[1] - src[1]
    dz = dst[2] - src[2]

    hyp = math.sqrt(dx * dx + dy * dy)

    yaw = math.degrees(math.atan2(dy, dx)) + 90
    pitch = math.degrees(math.atan2(dz, hyp))

    return yaw, pitch


def write_view_angles(local_player, yaw, pitch):
    pm.write_float(local_player + YAW, yaw)
    pm.write_float(local_player + PITCH, pitch)

def get_distance(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))

while True:
    try:
        local_player = pm.read_int(LOCAL_PLAYER)
        player_count = pm.read_int(PLAYER_COUNT)
        my_head = get_player_head_position(local_player)
        my_team = pm.read_int(local_player + TEAM_NUM)

        closest_dist = float('inf')
        target_angles = None

        entity_list_base = pm.read_int(ENTITY_LIST)

        for i in range(player_count):
            entity = pm.read_int(entity_list_base + (i * 0x4))

            if entity == 0 or entity == local_player:
                continue

            if pm.read_int(entity + IS_DEAD) != 0:
                continue

            enemy_team = pm.read_int(entity + TEAM_NUM)
            if enemy_team == my_team:
                continue

            enemy_head = get_player_head_position(entity)

            if enemy_head == (0.0, 0.0, 0.0):
                continue

            dist = get_distance(my_head, enemy_head)

            if dist < closest_dist:
                closest_dist = dist
                target_angles = calculate_angle(my_head, enemy_head)

        if target_angles:
            write_view_angles(local_player, *target_angles)

        time.sleep(0.01)

    except Exception as e:
        print("Error:", e)
        break
