from math import atan2, sqrt
from constants import *
import tkinter.ttk as ttk
import tkinter as tk
import optimizer
import simulator
import clipboard
import pygubu

def accept_multiline_input(terminator:str="DONE") -> str:
    all_lines = []
    while True:
        data = input("... ")
        if data != terminator:
            all_lines.append(data)
        else:
            break
    return "\n".join(all_lines)

def method_normal_pullup(initial_angle, initial_speed, facing, frames):
    c_angle, c_speed = initial_angle, initial_speed
    frame_data = []
    for _ in range(frames):
        angle = optimizer.find_best_vertical_input(c_angle, c_speed, facing)
        if c_angle > 90:
            if c_speed > MAX_SPEED:
                angle = 90
            else:
                angle = 0

        c_angle, c_speed = simulator.simulate(c_angle, c_speed, angle)
        frame_data.append(angle)
    
    return frame_data

def method_megajoule(initial_angle, initial_speed, facing, frames, target):
    ...

def method_manual_wiggle(initial_angle, initial_speed, facing, frames, wiggle_horizontal, wiggle_vertical):
    ...

class Glideline:
    def __init__(self, main=None):
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(".")
        builder.add_from_file("./main.ui")
        self.mainwindow = builder.get_object('mainWindow', main)
        builder.connect_callbacks(self)
    
        # builder.create_variable("wiggle_horizontal", "int")
        # builder.create_variable("wiggle_vertical", "int")

        self.default_setup()

    def default_setup(self):
        print("Running default window setup")
        method:ttk.Combobox = self.builder.get_object('method')
        method.current(0)

    def run(self):
        self.mainwindow.mainloop()
    
    def optimize(self):
        method:ttk.Combobox = self.builder.get_object('method')
        active_method = method.current()

        gamestate_box:tk.Entry = self.builder.get_object("gamestate")

        frame_count = self.builder.get_variable("frames").get()

        target = [
            self.builder.get_variable("target_x").get(),
            self.builder.get_variable("target_y").get()
        ]

        gamestate_data = gamestate_box.get("1.0", "end").rstrip().splitlines()
        speedIndex = [1 if x.startswith("Speed") else 0 for x in gamestate_data].index(1)
        speedString = gamestate_data[speedIndex][len("Speed: "):]
        speedX = float(speedString.split(", ")[0])
        speedY = float(speedString.split(", ")[1])
        facing = Facings.Left if speedX < 0 else Facings.Right # flip the x speed if facing left

        initial_speed = sqrt((speedX**2) + (speedY**2))
        initial_angle = (((atan2(speedY, speedX * facing.value) * RAD_TO_DEG) + 90) + 360) % 360

        if active_method == 0: # normal pullup
            frame_data = method_normal_pullup(initial_angle, initial_speed, facing, frame_count)
            self.set_output_text(optimizer.frameDataToInputs(frame_data))
        
        elif active_method == 1: # megajoule method
            self.set_output_text("Not yet implemented.")
        
        elif active_method == 2: # manual wiggle
            self.set_output_text("Not yet implemented.")

    def set_output_text(self, text):
        output_box:tk.Entry = self.builder.get_object("output")

        output_box.config(state="normal")
        output_box.insert("1.0", text)
        output_box.config(state="disabled")

    def copy_output(self):
        output:tk.Text = self.builder.get_object("output")
        clipboard.copy(output.get("1.0", "end").rstrip())
    
    def update_method(self, *args):
        print(args)

if __name__ == "__main__":
    app = Glideline()
    app.run()