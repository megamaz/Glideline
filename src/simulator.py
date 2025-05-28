from utilities import *
from math import atan2, sin, cos

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

    init_state:tuple

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

        windIndex =[1 if x.startswith(
            "Wind") else 0 for x in gamestate_data].index(1)
        windString = gamestate_data[windIndex][len("Wind: "):]
        self.wind_x, self.wind_y = (
            float(windString.split(", ")[0])/10,
            float(windString.split(", ")[1])/10
        )

        self.init_state = (self.pos_x, self.pos_y, self.speed, self.angle, self.wind_x, self.wind_y, self.facing.value)
    
    @classmethod
    def from_direct(cls, pos_x:float, pos_y:float, speed:float, angle:float, wind_x:float, wind_y:float, facing:int) -> "State":
        new = State.__new__(State)
        new.pos_x, new.pos_y, new.speed, new.angle, new.wind_x, new.wind_y, new.facing = pos_x, pos_y, speed, angle, wind_x, wind_y, Facings(facing)
        new.init_state = (pos_x, pos_y, speed, angle, wind_x, wind_y, facing)
        return new
    
    def clone_state(self) -> "State":
        return State.from_direct(*self.init_state)

    def step(self, angle:float):
        self.angle, self.speed = simulate(self.angle, self.speed, angle)
        
        self.pos_x += (self.speed * sin(self.angle * DEG_TO_RAD) + self.wind_x) * DELTA_TIME * self.facing.value
        self.pos_y -= (self.speed * cos(self.angle * DEG_TO_RAD) + self.wind_y) * DELTA_TIME
    
    def reset_state(self):
        self.pos_x, self.pos_y, self.speed, self.angle, self.wind_x, self.wind_y, facing_val = self.init_state
        self.facing = Facings(facing_val)
