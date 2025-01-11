from utilities import *

def simulate(initial_speed:float, initial_angle:float, angle:float) -> tuple:
    """Simulates elytra speed and angle changes. Does not take stable_timer into account.

    Params (all degrees are in feather degrees)
    - `initial_speed` the initial speed.
    - `initial_angle` the angle you are currently flying at, in the range of 0-180
    - `angle` the angle held on the controller. 0 degrees is fully up, and 90 is fully right (clockwise)
    
    Returns a tuple:
    - new_speed, new_angle
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
    # new_angle = Clamp(new_angle, ((STABLE_ANGLE - halfrange) * RAD_TO_DEG) + 90, ((STABLE_ANGLE + halfrange) * RAD_TO_DEG) + 90)

    if sin((new_angle - 90) * DEG_TO_RAD) < sin(STABLE_ANGLE):
        decel = FAST_DECEL if initial_speed > MAX_SPEED else DECEL
        new_speed = Approach(initial_speed, MIN_SPEED, DELTA_TIME * decel * abs(yInput))
        
    else:
        if initial_speed < MAX_SPEED:
            new_speed = Approach(initial_speed, MAX_SPEED, DELTA_TIME * ACCEL * abs(yInput))

    return new_speed, new_angle