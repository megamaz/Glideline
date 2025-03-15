from math import atan2, sqrt, sin, cos
from tkinter import messagebox
from constants import *
from utilities import *
import tkinter.ttk as ttk
import tkinter as tk
import webbrowser
import optimizer
import simulator
import clipboard
import pygubu
import os

def method_normal_pullup(initial_angle: float, initial_speed: float, facing: Facings, frames: int) -> list[float]:
    c_angle, c_speed = initial_angle, initial_speed
    frame_data = []
    for _ in range(frames):
        angle = optimizer.find_best_vertical_input(c_angle, c_speed, facing)

        c_angle, c_speed = simulator.simulate(c_angle, c_speed, angle)
        frame_data.append(angle)

    return frame_data


def method_megajoule(initial_angle:float, initial_speed:float, facing:Facings, frames:int, init_pos:list[float], target:list[float]) -> tuple[list[float]]:
    # returns (earliest time, highest speed)

    frame_data_earliest = []
    frame_data_fastest = []
    best_speed = 0
    best_time = float("inf")

    init_H = 1
    init_S = 1
    H = 1
    S = 1
    under_ratio = None
    over_ratio = None
    last_diff = 0
    closest = float("inf")
    options = 0
    while True:
        end_all = False
        arrived = False
        d2, d1 = 0, 0
        pos = list(init_pos)
        inputs_angles = []
        current_speed, current_angle = initial_speed, initial_angle
        f = 0
        midpoint = 0

        # Level out before starting algorithm
        if current_angle > 90:
            frame_data = method_normal_pullup(current_angle, current_speed, facing, 200)
        else:
            frame_data = [90,] * 100
        
        delay = -1
        for i in range(200):
            current_angle, current_speed = simulator.simulate(current_angle, current_speed, frame_data[i])
            pos[0] += current_speed * sin(current_angle * DEG_TO_RAD) * DELTA_TIME * facing.value
            pos[1] -= current_speed * cos(current_angle * DEG_TO_RAD) * DELTA_TIME
            inputs_angles.append(frame_data[i])
            f += 1
            if abs(90.0 - current_angle) <= 1.0 and delay < 0:
                midpoint = (pos[0] + target[0]) / 2
                break
            
        # First half of flight path
        frame_data = method_manual_wiggle(current_angle, current_speed, facing, 200, H, S, 0)
        for i in range(200):
            if pos[0] * facing.value > midpoint * facing.value:
                break
        
            current_angle, current_speed = simulator.simulate(current_angle, current_speed, frame_data[i])
            pos[0] += current_speed * sin(current_angle * DEG_TO_RAD) * DELTA_TIME * facing.value
            pos[1] -= current_speed * cos(current_angle * DEG_TO_RAD) * DELTA_TIME
            inputs_angles.append(frame_data[i])
            f += 1

        # Kill the optimizer if the ratio is longer than our flight path
        if H + S > f:
            break

        # Second half of flight path
        # The offset is equal to the VERTICAL pullup
        # This is to ensure that we properly reverse the ratio and start on horizontal rather than vertical
        frame_data = method_manual_wiggle(current_angle, current_speed, facing, 200, S, H, H)
        for i in range(200):
            current_angle, current_speed = simulator.simulate(current_angle, current_speed, frame_data[i])
            pos[0] += current_speed * sin(current_angle * DEG_TO_RAD) * DELTA_TIME * facing.value
            pos[1] -= current_speed * cos(current_angle * DEG_TO_RAD) * DELTA_TIME
            inputs_angles.append(frame_data[i])
            f += 1

            if dist(pos, target) <= current_speed * DELTA_TIME:
                arrived = True
                break
            if pos[0] * facing.value > target[0] * facing.value:
                break
        
        # If we're arrived do some math shenanigans to try some other ratios
        if arrived:
            print(f"{H}f/{S}f+{d1} -> {S}f/{H}f+{d1} succeeded in f{f}, speed={current_speed}")
            if current_speed > best_speed:
                closest = -1
                best_speed = current_speed
                frame_data_fastest = list(inputs_angles)
            if f < best_time:
                closest = -1
                best_time = f
                frame_data_earliest = list(inputs_angles)
            
            if target[1] < init_pos[1]: # target is above us
                init_H += 1
                H = init_H
                S = 1
                over_ratio = None
                under_ratio = None
            else:
                init_S += 1
                H = 1
                S = init_S
                over_ratio = None
                under_ratio = None
        else:
            # print(f"{H}f/{S}f+{d1} -> {S}f/{H}f+{d2} failed: Y diff from target {abs(pos[1] - target[1])} ({'undershot' if pos[1] > target[1] else 'overshot'})")
            if abs(pos[1] - target[1]) < closest:
                closest = abs(pos[1] - target[1])

            if pos[1] > target[1]:
                under_ratio = (H, S)
                S += 1
            else:
                over_ratio = (H, S)
                H += 1
            
            if over_ratio and under_ratio:
                new_ratio = ((over_ratio[0] + under_ratio[0])/2, (over_ratio[1] + under_ratio[1])/2)
                if new_ratio[0] % 1 != 0 or new_ratio[1] % 1 != 0:
                    new_ratio = (new_ratio[0]*2, new_ratio[1]*2)
                H, S = new_ratio
                under_ratio = None
                over_ratio = None
            
            if abs(pos[1] - target[1]) == last_diff:
                break

            last_diff = abs(pos[1] - target[1])
            
        options += 1

    print(f"Done, tried {options} ratios")
    return frame_data_fastest, frame_data_earliest


def method_manual_wiggle(initial_angle: float, initial_speed: float, facing: Facings, frames: int, wiggle_horizontal: int, wiggle_vertical: int, wiggle_offset: int) -> list[float]:
    wiggling = False  # I have some really silly variable names
    # False means we're stabilizing, True means we're going horizontal
    wiggle_countdown = wiggle_vertical
    # do the offset
    # this should always be a whole number anyways
    # even if it's a float
    for _ in range(int(wiggle_offset)):
        wiggle_countdown -= 1
        if wiggle_countdown <= 0:
            wiggling = not wiggling
            if wiggling:
                wiggle_countdown = wiggle_horizontal
            else:
                wiggle_countdown = wiggle_vertical

    frame_data = []
    c_angle, c_speed = initial_angle, initial_speed
    for f in range(frames):
        angle_hold = 0
        if wiggling:
            angle_hold = 90.0 if facing == Facings.Right else 270.0
        else:
            angle_hold = optimizer.find_best_vertical_input(c_angle, c_speed, facing)

        frame_data.append(angle_hold)
        c_angle, c_speed = simulator.simulate(c_angle, c_speed, angle_hold)

        wiggle_countdown -= 1
        if wiggle_countdown == 0:
            wiggling = not wiggling
            if wiggling:
                wiggle_countdown = wiggle_horizontal
            else:
                wiggle_countdown = wiggle_vertical

    return frame_data


class Glideline:
    def __init__(self, main=None):
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(".")
        builder.add_from_file("./main.ui")
        self.mainwindow:tk.Tk = builder.get_object('mainWindow', main)
        builder.connect_callbacks(self)

        self.input_data_mj = [[0,], [0,]]
        self.last_method = 0

        self.couldnt_path_msg = "Couldn't path to target.\nAutomated Wiggles are better at long, horizontal\ndistances.\nIf your scenario doesn't fit that description,\nthen you should stick to manual wiggles and\noptimal pullups."

        version_f = open("./version.txt", "r", encoding="utf-8")
        version = version_f.read()
        version_f.close()
        self.mainwindow.title(f"Glideline {version}")

        self.default_setup()


    def default_setup(self):
        print("Running default window setup")
        method: ttk.Combobox = self.builder.get_object('method')
        method.current(0)

        mj_method: ttk.Combobox = self.builder.get_object('mj_method')
        mj_method.current(0)

    def run(self):
        # check if first time running
        first_launch = not os.path.exists("./firstlaunch")
        if first_launch:
            open("./firstlaunch", "w").close()
            self.mainwindow.after(0, self.info)
        self.mainwindow.mainloop()

    def optimize(self):
        method: ttk.Combobox = self.builder.get_object('method')
        active_method = method.current()
        self.last_method = active_method

        gamestate_box: tk.Entry = self.builder.get_object("gamestate")

        frame_count = self.builder.get_variable("frames").get()

        target = [
            self.builder.get_variable("target_x").get(),
            self.builder.get_variable("target_y").get()
        ]

        hotkey = self.builder.get_variable("hotkey").get()

        gamestate_data = gamestate_box.get("1.0", "end").rstrip().splitlines()

        speedIndex = [1 if x.startswith(
            "Speed") else 0 for x in gamestate_data].index(1)
        speedString = gamestate_data[speedIndex][len("Speed: "):]
        speedX = float(speedString.split(", ")[0])
        speedY = float(speedString.split(", ")[1])
        # flip the x speed if facing left
        facing = Facings.Left if speedX < 0 else Facings.Right

        initial_speed = sqrt((speedX**2) + (speedY**2))
        initial_angle = (
            ((atan2(speedY, speedX * facing.value) * RAD_TO_DEG) + 90) + 360) % 360

        posIndex = [1 if x.startswith(
            "Pos") else 0 for x in gamestate_data].index(1)
        posString = gamestate_data[posIndex][len("Pos: "):]
        position = [
            float(posString.split(", ")[0]),
            float(posString.split(", ")[1])
        ]

        # get manual wiggle data
        wiggle_horizontal = self.builder.get_variable("wiggle_horizontal").get()
        wiggle_vertical = self.builder.get_variable("wiggle_vertical").get()
        wiggle_offset = self.builder.get_variable("wiggle_offset").get()

        if active_method == 0:  # normal pullup
            frame_data = method_normal_pullup(
                initial_angle, initial_speed, facing, frame_count)
            self.set_output_text(optimizer.frameDataToInputs(frame_data, hotkey))

        elif active_method == 1:  # megajoule method
            mj_selection: ttk.Combobox = self.builder.get_object('mj_method')
            self.input_data_mj[0], self.input_data_mj[1] = method_megajoule(initial_angle, initial_speed, facing, frame_count, position, target)
            # mj might not arrive at the target
            # need to account for that
            # if it doesn't, then both input_data_mj[0] and [1] will be empty
            if len(self.input_data_mj[0]) == 0:
                self.set_output_text(self.couldnt_path_msg)
                return
            
            self.set_output_text(optimizer.frameDataToInputs(self.input_data_mj[mj_selection.current()], hotkey))

        elif active_method == 2:  # manual wiggle
            frame_data = method_manual_wiggle(initial_angle, initial_speed, facing, frame_count, wiggle_horizontal, wiggle_vertical, wiggle_offset)
            self.set_output_text(optimizer.frameDataToInputs(frame_data, hotkey))

    def set_output_text(self, text):
        output_box: tk.Entry = self.builder.get_object("output")
        output_box.config(state="normal")
        output_box.delete("1.0", "end")
        output_box.insert("1.0", text)
        output_box.config(state="disabled")

    def copy_output(self):
        output: tk.Text = self.builder.get_object("output")
        clipboard.copy(output.get("1.0", "end").rstrip())

    def mj_new_selection(self, *args):
        # only change text if last mathod was mj
        if self.last_method == 1:
            hotkey = self.builder.get_variable("hotkey").get()
            mj_selection: ttk.Combobox = self.builder.get_object('mj_method')
            
            if len(self.input_data_mj[mj_selection.current()]) == 0:
                self.set_output_text(self.couldnt_path_msg)
                return

            self.set_output_text(optimizer.frameDataToInputs(self.input_data_mj[mj_selection.current()], hotkey))
    
    def info(self):
        box = messagebox.showinfo("How To Use", open("./infobox.txt", "r", encoding="utf-8").read())
    
    def doc_clipboard(self):
        webbrowser.open_new("https://docs.google.com/document/d/1xFF6wjdig5k9vOUF3mAvvWh4pF2HBvOw5PJ-aCNNeTo")


if __name__ == "__main__":
    app = Glideline()
    app.run()