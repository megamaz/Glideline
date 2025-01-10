from math import sin, cos, pi, sqrt, atan2, acos
from enum import Enum
from constants import *
import time

##############################################################
############ VARIABLES YOU WANNA MODIFY AS A USER ############
##############################################################

ELYTRA_HOTKEY = "PE" # change this if you're using PP or something else
PRECISION_OUT = 4 # how many digits of precision are printed to the console
PRECISION_COMPUTE = 12 # how many digits of precision are calculated (breaks down at 17 but you shouldn't need more than 12)
HOLD_JUMP = False # this can allow you to get more height
JUMP_KEY = "J"
STOP_VALUE = 0.001 # values below this number will NOT be added to output.
DO_WIGGLE = False # whether or not to wiggle. You'll get an error if your frames below aren't setup right.
WIGGLE_FRAMES_HORIZONTAL = 2 # these two variables control the wiggle. horizontal controls the amount of frames where we hold 90 / 270, and stabilizer is the amount of frames we hold up to change our direction.
WIGGLE_FRAMES_STABILIZER = 2 # if DO_WIGGLE is true, neither of these should be 0.

##############################################################
############ VARIABLES YOU WANNA MODIFY AS A USER ############
##############################################################

def frange(min, max, step):
    value = min
    while value < max:
        value += step
        yield value

def Approach(value, target, step):
    if value > target:
        return max(value - step, target)
    elif value < target:
        return min(value + step, target)
    return target

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

def optimizer(initial_angle, initial_speed, facing, frames=100, do_wiggle=False, wig_frames_horizontal=0, wig_frames_stabilizer=0) -> str:
    output = ""

    wiggling = False # I have some really silly variable names
                        # False means we're stabilizing, True means we're going horizontal
    wiggle_countdown = max(wig_frames_horizontal, wig_frames_stabilizer) # I'm pissing myself
    for f in range(frames):

        maxAngleChange = DELTA_TIME * MAX_ANGLE_CHANGE_INV_SPEED_FACTOR / initial_speed
        
        angle_min = 0
        # if we're moving "down" but above the stable angle
        # then we don't want to optimize for immediate height
        if initial_angle > 90 and initial_angle < 90 + STABLE_ANGLE_DEG:
            angle_min = (acos((STABLE_ANGLE - (((initial_angle - 90) * pi)/180.0))))*RAD_TO_DEG - (maxAngleChange * RAD_TO_DEG)
        angle_max = 180
        
        init_min_angle = angle_min
        init_max_angle = angle_max

        best_yspeed = float("inf") # best speed gotten
        best_xspeed = float("inf")
        best_total_speed = float("inf")
        best_angleI = 0 # best angle INPUT
        best_angleF = 0 # best angle FLIGHT
        step_size = 1
        iteration = 1

        end_prematurely = False # flag to end immediately
        while iteration < PRECISION_COMPUTE and not end_prematurely:
            for angle in frange(angle_min, angle_max, step_size):
                # we want to prioritize more horizontal angles since that means less speed loss
                # this ensures that if a more vertical angle gives the same speed as a more horizontal one, the more horizontal one is picked
                # less speed loss
                if initial_angle < 180:
                    angle = angle_max - angle + angle_min
                
                # if we're flying down then we want to optimize for long-term speed
                if initial_angle > 90 + STABLE_ANGLE_DEG and initial_speed <= MAX_SPEED:
                    angle = 0
                    end_prematurely = True

                # wiggle
                if wiggling:
                    angle = 90
                    end_prematurely = True


                # simulate in-game speed changes
                halfrange = ANGLE_RANGE / 2.0
                newSpeed = initial_speed
                yInput = -sin((angle + 90) * DEG_TO_RAD)

                target = ((STABLE_ANGLE + halfrange * yInput) * RAD_TO_DEG) + 90
                newAngle = Approach(initial_angle, target, (maxAngleChange * RAD_TO_DEG))

                if sin((newAngle - 90) * DEG_TO_RAD) < sin(STABLE_ANGLE):
                    decel = FAST_DECEL if initial_speed > MAX_SPEED else DECEL
                    newSpeed = Approach(initial_speed, MIN_SPEED, DELTA_TIME * decel * abs(yInput))
                    
                else:
                    if initial_speed < MAX_SPEED:
                        newSpeed = Approach(initial_speed, MAX_SPEED, DELTA_TIME * ACCEL * abs(yInput))

                ySpeed = newSpeed * -sin((90 - newAngle) * DEG_TO_RAD)

                # since y speed is negative when moving up
                if ySpeed < best_yspeed:
                    best_yspeed = ySpeed
                    best_total_speed = newSpeed
                    best_angleI = angle
                    best_angleF = newAngle
                
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
        # update the values for the next frame
        initial_angle = best_angleF
        initial_speed = best_total_speed

        angle_hold = best_angleI
        if facing == Facings.Left:
            angle_hold = ((-best_angleI)%360)
        
        output += f"   1{f',{JUMP_KEY}' if HOLD_JUMP else ''},{ELYTRA_HOTKEY},F,{angle_hold:.{PRECISION_OUT}f}\n"

        # Wiggling
        if do_wiggle:
            wiggle_countdown -= 1
            if wiggle_countdown <= 0:
                wiggling = not wiggling
                if wiggling:
                    wiggle_countdown = wig_frames_horizontal
                else:
                    wiggle_countdown = wig_frames_stabilizer

        
    new_out = sanitizer(output)
    # new_out.append(f"9999{f',{JUMP_KEY}' if HOLD_JUMP else ''},{ELYTRA_HOTKEY},F,{0.0:.{PRECISION_OUT}f}")

    return "\n".join(new_out)

def main():
    data = []
    print("Elytra Optimizer - if you run into issues, ping megamaz.\nFor more control over the output, check the variables at the start of the program to make sure they fit what you want to do.\nThe comments should explain what each of them does.\n")

    # Verify variables aren't setup wrong
    if DO_WIGGLE:
        assert WIGGLE_FRAMES_HORIZONTAL > 0 and WIGGLE_FRAMES_STABILIZER > 0, "One of your WIGGLE_FRAMES variables is at or below 0. Make sure they are at least 1. If you don't want to wiggle, then set DO_WIGGLE to False."

    print("Paste CelesteTAS Info here (hit enter twice when done):\n")
    while True:
        info = input("")
        if info != "":
            data.append(info)
        else:
            break
    
    speedIndex = [1 if x.startswith("Speed") else 0 for x in data].index(1)
    speedString = data[speedIndex][len("Speed: "):]
    speedX = float(speedString.split(", ")[0])
    speedY = float(speedString.split(", ")[1])
    facing = Facings.Left if speedX < 0 else Facings.Right # flip the x speed if facing left

    initial_speed = sqrt((speedX**2) + (speedY**2))
    initial_angle = (((atan2(speedY, speedX * facing.value) * RAD_TO_DEG) + 90) + 360) % 360
    # (x+360)%360 to remap to range [0-360] instead of [-180, 180]
    print(f"initial flight angle: {initial_angle}\ninitial flight speed: {initial_speed}\n\n")

    start = time.time()
    result = optimizer(initial_angle, initial_speed, facing, 100, DO_WIGGLE, WIG_FRAMES_HORIZONTAL, WIG_FRAMES_STABILIZER)

    print(result)


    input(f"\nDone in {time.time() - start}s.\nHit enter to start new session.")
