from math import sin, cos, pi, sqrt, atan2, acos
from enum import Enum
from constants import *
from utilities import *
import simulator

ELYTRA_HOTKEY = "PE"  # change this if you're using PP or something else
PRECISION_OUT = 4  # how many digits of precision are printed to the console
# how many digits of precision are calculated (breaks down at 17 but you shouldn't need more than 12)
PRECISION_COMPUTE = 12
HOLD_JUMP = False  # this can allow you to get more height
JUMP_KEY = "J"
STOP_VALUE = 0.001  # values below this number will NOT be added to output.
# whether or not to wiggle. You'll get an error if your frames below aren't setup right.
DO_WIGGLE = False
# these two variables control the wiggle. horizontal controls the amount of frames where we hold 90 / 270, and stabilizer is the amount of frames we hold up to change our direction.
WIGGLE_FRAMES_HORIZONTAL = 2
# if DO_WIGGLE is true, neither of these should be 0.
WIGGLE_FRAMES_STABILIZER = 2

# "santize" output (combine frames with repeated inputs)
def sanitizer(output):
    new_out = [output.splitlines()[0]]
    for line in output.splitlines()[1:]:
        # check if the angles are identical
        angle = line.split(",")[-1]
        if angle == new_out[-1].split(",")[-1]:
            length = int(new_out[-1].split(",")[0].strip())
            length += 1
            new_out[-1] = f"{length:4}{f',{JUMP_KEY}' if HOLD_JUMP else ''},{ELYTRA_HOTKEY},F,{angle}"
        else:
            new_out.append(line)

    return new_out


def inputStringToFrameData(string) -> list[float]:
    frame_data = []
    t_data = []
    for w in string.splitlines():
        t_data.append((int(w.lstrip().split(",")[0]), float(w.split(",")[-1])))
    for t in t_data:
        for _ in range(t[0]):
            frame_data.append(t[1])

    return frame_data


def frameDataToInputs(frame_data, hotkey:str, precision:int=4) -> str:
    out = ""
    for f in frame_data:
        out += f"   1,{hotkey},F,{f:.{precision}f}".rstrip("0").rstrip(".") + "\n"

    return "\n".join(sanitizer(out))


def find_best_vertical_input(initial_angle: float, initial_speed: float, facing: Facings) -> float:
    """Finds the best input (in feather degrees) to maximize vertical velocity given the frame.
    - `initial_angle` : the initial flying angle in feather degrees.
    - `initial_speed` : the initial speed of the elytra.
    - `facing` the facing direction."""

    maxAngleChange = maxAngleChangeFormula(initial_speed)

    angle_min = 0
    # if we're moving "down" but above the stable angle
    # then we don't want to optimize for immediate height
    if initial_angle > 90 and initial_angle < 90 + STABLE_ANGLE_DEG:
        angle_min = (acos((STABLE_ANGLE - (((initial_angle - 90) * pi)/180.0))))*RAD_TO_DEG - (maxAngleChange * RAD_TO_DEG)
    angle_max = 180

    init_min_angle = angle_min
    init_max_angle = angle_max

    best_yspeed = float("inf")  # best speed gotten
    best_total_speed = float("inf")
    best_angleI = 0  # best angle INPUT
    best_angleF = 0  # best angle FLIGHT
    step_size = 1
    iteration = 1

    end_prematurely = False
    while iteration < PRECISION_COMPUTE:
        for angle in frange(angle_min, angle_max, step_size):
            if initial_angle < 180:
                angle = angle_max - angle + angle_min
            # simulate in-game speed changes
            new_angle, new_speed = simulator.simulate(initial_angle, initial_speed, angle)
            ySpeed = new_speed * -sin((90 - new_angle) * DEG_TO_RAD)

            # if we're flying down then we want to optimize for long-term speed
            if initial_angle > 90 + STABLE_ANGLE_DEG and initial_speed <= MAX_SPEED:
                angle = 0
                end_prematurely = True

            # since y speed is negative when moving up
            if ySpeed < best_yspeed:
                best_yspeed = ySpeed
                best_total_speed = new_speed
                best_angleI = angle
                best_angleF = new_angle

            if end_prematurely:
                break

        # once we've found our best angle for this frame, narrow down precision
        angle_min = best_angleI - 10/(10**iteration)
        angle_max = best_angleI + 10/(10**iteration)

        # prevent angles from exiting the bounds of their initial values
        angle_min = max(init_min_angle, angle_min)
        best_angleI = max(init_min_angle, best_angleI)
        angle_max = min(init_max_angle, angle_max)
        best_angleI = min(init_max_angle, best_angleI)

        step_size /= 10.0

        iteration += 1

    initial_angle = best_angleF
    initial_speed = best_total_speed

    angle_hold = best_angleI
    if facing == Facings.Left:
        angle_hold = ((-best_angleI) % 360)

    return angle_hold
