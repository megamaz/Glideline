from utilities import *
from math import atan2

def simulate(initial_angle:float, initial_speed:float, angle:float) -> tuple:
    """Simulates elytra speed and angle changes. Does not take stable_timer into account.

    Params (all degrees are in feather degrees)
    - `initial_speed` the initial speed.
    - `initial_angle` the angle you are currently flying at, in the range of 0-180
    - `angle` the angle held on the controller. 0 degrees is fully up, and 90 is fully right (clockwise)
    
    Returns a tuple:
    - new_angle, new_speed
    """
    maxAngleChange = maxAngleChangeFormula(initial_speed)
    
    halfrange = ANGLE_RANGE / 2.0
    new_speed = initial_speed
    yInput = -sin((angle + 90) * DEG_TO_RAD)

    if initial_speed == MIN_SPEED and yInput < 0:
        new_angle = Approach(initial_angle, (STABLE_ANGLE * RAD_TO_DEG) + 90, maxAngleChange * RAD_TO_DEG)
    else:
        target = ((STABLE_ANGLE + halfrange * yInput) * RAD_TO_DEG) + 90
        new_angle = Approach(initial_angle, target, (maxAngleChange * RAD_TO_DEG))
    new_angle = Clamp(new_angle, ((STABLE_ANGLE - halfrange) * RAD_TO_DEG) + 90, ((STABLE_ANGLE + halfrange) * RAD_TO_DEG) + 90)

    if sin((new_angle - 90) * DEG_TO_RAD) < sin(STABLE_ANGLE):
        decel = FAST_DECEL if initial_speed > MAX_SPEED else DECEL
        new_speed = Approach(initial_speed, MIN_SPEED, DELTA_TIME * decel * abs(yInput))
        
    else:
        if initial_speed < MAX_SPEED:
            new_speed = Approach(initial_speed, MAX_SPEED, DELTA_TIME * ACCEL * abs(yInput))

    return new_angle, new_speed

class State:
    speed:float
    angle:float
    facing:Facings
    pos_x:float
    pos_y:float

    wind_x:float
    wind_y:float

    def __init__(self, st_string:str):
        """Parses a CelesteTAS State string as a State object."""
        gamestate_data = st_string.strip().splitlines()
        speedIndex = [1 if x.startswith(
            "Speed") else 0 for x in gamestate_data].index(1)
        speedString = gamestate_data[speedIndex][len("Speed: "):]
        speedX = float(speedString.split(", ")[0])
        speedY = float(speedString.split(", ")[1])
        # flip the x speed if facing left
        self.facing = Facings.Left if speedX < 0 else Facings.Right

        self.speed = sqrt((speedX**2) + (speedY**2))
        self.angle = (
            ((atan2(speedY, speedX * self.facing.value) * RAD_TO_DEG) + 90) + 360) % 360

        posIndex = [1 if x.startswith(
            "Pos") else 0 for x in gamestate_data].index(1)
        posString = gamestate_data[posIndex][len("Pos: "):]
        self.pos_x, self.pos_y = (
            float(posString.split(", ")[0]),
            float(posString.split(", ")[1])
        )
