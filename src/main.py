from math import atan2, sqrt
from constants import *
import tkinter.ttk as ttk
import tkinter as tk
import optimizer
import simulator
import clipboard
import pygubu


def method_normal_pullup(initial_angle: float, initial_speed: float, facing: Facings, frames: int) -> list[float]:
    c_angle, c_speed = initial_angle, initial_speed
    frame_data = []
    for _ in range(frames):
        if c_angle >= 90 + STABLE_ANGLE_DEG and c_speed <= MAX_SPEED:
            angle = 0.0
        else:
            angle = optimizer.find_best_vertical_input(c_angle, c_speed, facing)

        c_angle, c_speed = simulator.simulate(c_angle, c_speed, angle)
        frame_data.append(angle)

    return frame_data


def method_megajoule(initial_angle:float, initial_speed:float, facing:Facings, frames:int, target:list[float]):
    ...


def method_manual_wiggle(initial_angle: float, initial_speed: float, facing: Facings, frames: int, wiggle_horizontal: int, wiggle_vertical: int, wiggle_offset: int) -> list[float]:
    wiggling = False  # I have some really silly variable names
    # False means we're stabilizing, True means we're going horizontal
    wiggle_countdown = wiggle_vertical
    # do the offset
    for _ in range(wiggle_offset):
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
            angle_hold = optimizer.find_best_vertical_input(
                c_angle, c_speed, facing)

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
        self.mainwindow = builder.get_object('mainWindow', main)
        builder.connect_callbacks(self)

        self.default_setup()

    def default_setup(self):
        print("Running default window setup")
        method: ttk.Combobox = self.builder.get_object('method')
        method.current(0)

    def run(self):
        self.mainwindow.mainloop()

    def optimize(self):
        method: ttk.Combobox = self.builder.get_object('method')
        active_method = method.current()

        gamestate_box: tk.Entry = self.builder.get_object("gamestate")

        frame_count = self.builder.get_variable("frames").get()

        target = [
            self.builder.get_variable("target_x").get(),
            self.builder.get_variable("target_y").get()
        ]

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

        # get manual wiggle data
        wiggle_horizontal = self.builder.get_variable("wiggle_horizontal").get()
        wiggle_vertical = self.builder.get_variable("wiggle_vertical").get()
        wiggle_offset = self.builder.get_variable("wiggle_offset").get()

        if active_method == 0:  # normal pullup
            frame_data = method_normal_pullup(
                initial_angle, initial_speed, facing, frame_count)
            self.set_output_text(optimizer.frameDataToInputs(frame_data))

        elif active_method == 1:  # megajoule method
            self.set_output_text("Not yet implemented.")

        elif active_method == 2:  # manual wiggle
            frame_data = method_manual_wiggle(initial_angle, initial_speed, facing, frame_count, wiggle_horizontal, wiggle_vertical, wiggle_offset)
            self.set_output_text(optimizer.frameDataToInputs(frame_data))

    def set_output_text(self, text):
        output_box: tk.Entry = self.builder.get_object("output")
        output_box.config(state="normal")
        output_box.delete("1.0", "end")
        output_box.insert("1.0", text)
        output_box.config(state="disabled")

    def copy_output(self):
        output: tk.Text = self.builder.get_object("output")
        clipboard.copy(output.get("1.0", "end").rstrip())

    def update_method(self, *args):
        print(args)


if __name__ == "__main__":
    app = Glideline()
    app.run()
