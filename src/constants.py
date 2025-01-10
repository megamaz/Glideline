from math import pi
from enum import Enum

DELTA_TIME = 0.016666699201 # the exact in-game value when running at 60fps
MAX_ANGLE_CHANGE_INV_SPEED_FACTOR = 480.0
MIN_SPEED = 64.0
MAX_SPEED = 320.0
DECEL = 165.0
FAST_DECEL = 220.0
ACCEL = 90.0
STABLE_ANGLE = 0.2
ANGLE_RANGE = 2.0
RAD_TO_DEG = 180.0 / pi
DEG_TO_RAD = pi / 180.0
STABLE_ANGLE_DEG = STABLE_ANGLE * RAD_TO_DEG
STABLE_ANGLE_DEG_LEFT = (-STABLE_ANGLE_DEG + 360) % 360

class Facings(Enum):
    Left = -1
    Right = 1