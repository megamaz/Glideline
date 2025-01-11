from constants import *
from math import sin, asin, sqrt

def maxAngleChangeFormula(speed):
    if speed == 0.0:
        return float("inf")
    return DELTA_TIME * MAX_ANGLE_CHANGE_INV_SPEED_FACTOR / speed

def FlightAngleToInput(angle):
    invalue = -(((angle - 90) * DEG_TO_RAD) - STABLE_ANGLE)
    if invalue <= -1:
        return 180 
    elif invalue >= 1:
        return 0
    return -(asin(invalue) * RAD_TO_DEG - 90)

def InputToFlightAngle(angle):
    return ((STABLE_ANGLE - sin((angle + 90) * DEG_TO_RAD)) * RAD_TO_DEG) + 90

def Approach(value, target, step):
    if value > target:
        return max(value - step, target)
    elif value < target:
        return min(value + step, target)
    return target

def Clamp(value, min_value, max_value):
    return min(max(value, min_value), max_value)

def dist(a, b):
    return sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)

