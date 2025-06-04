from math import atan2, sqrt, sin, cos
from tkinter import messagebox
from simulator import State
from constants import *
from utilities import *
import tkinter.ttk as ttk
import tkinter as tk
import agent_module
import webbrowser
import optimizer
import clipboard
import logging
import random
import pygubu
import time
import sys
import os

class ColorFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',   # blue
        'INFO': '', # regular
        'WARNING': '\033[93m', # yellow
        'ERROR': '\033[91m',   # red
        'CRITICAL': '\033[95m' # magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        msg = super().format(record)
        return f"{color}{msg}{self.RESET}"

def setup_logging():
    print("Setting up Python logger")
    level = logging.DEBUG if "--debug" in sys.argv else logging.INFO

    string_format = "[%(asctime)s.%(msecs)03d %(levelname)s %(module)s.%(funcName)s]: %(message)s"
    string_datefmt = "%H:%M:%S"
    console = logging.StreamHandler()
    file = logging.FileHandler("../_latest.log", "w")
    
    file.setFormatter(logging.Formatter(string_format, datefmt=string_datefmt))
    console.setFormatter(ColorFormatter(string_format, datefmt=string_datefmt))
    
    file.setLevel(logging.DEBUG)
    console.setLevel(level)

    logging.basicConfig(handlers=[console, file])
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info("Python logger setup, sending to C++")

    agent_module.setup_logger(logging)


def method_normal_pullup(init_state:State, frames: int) -> list[float]:
    logging.info("Running normal pullup method")
    state = init_state.clone_state()
    frame_data = []
    for _ in range(frames):
        angle = optimizer.find_best_vertical_input(state.angle, state.speed, init_state.facing)
        state.step(angle)
        frame_data.append(angle)

    return frame_data


def method_megajoule(init_state:State, frames:int, target:list[float]) -> tuple[list[float]]:
    logging.info("Running megajoule method")
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
    state = init_state.clone_state()
    while True:
        end_all = False
        arrived = False
        d2, d1 = 0, 0
        inputs_angles = []
        f = 0
        midpoint = 0

        # Level out before starting algorithm
        if state.angle > 90:
            frame_data = method_normal_pullup(init_state, 200)
        else:
            frame_data = [90,] * 100
        
        delay = -1
        for i in range(200):
            state.step(frame_data[i])
            
            inputs_angles.append(frame_data[i])
            f += 1
            if abs(90.0 - state.angle) <= 1.0 and delay < 0:
                midpoint = (state.pos_x + target[0]) / 2
                break
            
        # First half of flight path
        frame_data = method_manual_wiggle(init_state, 200, H, S, 0)
        for i in range(200):
            if state.pos_x * state.facing.value > midpoint * init_state.facing.value:
                break
                
            state.step(frame_data[i])
            inputs_angles.append(frame_data[i])
            f += 1

        # Kill the optimizer if the ratio is longer than our flight path
        if H + S > f:
            break

        # Second half of flight path
        # The offset is equal to the VERTICAL pullup
        # This is to ensure that we properly reverse the ratio and start on horizontal rather than vertical
        frame_data = method_manual_wiggle(init_state, 200, S, H, H)
        for i in range(200):
            state.step(frame_data[i])
            inputs_angles.append(frame_data[i])
            f += 1

            if dist([state.pos_x, state.pos_y], target) <= state.speed * DELTA_TIME:
                arrived = True
                break
            if state.pos_x * init_state.facing.value > target[0] * init_state.facing.value:
                break
        
        # If we're arrived do some math shenanigans to try some other ratios
        if arrived:
            logging.info(f"{H}f/{S}f+{d1} -> {S}f/{H}f+{d1} succeeded in {f}f, speed={state.speed}")
            if state.speed > best_speed:
                closest = -1
                best_speed = state.speed
                frame_data_fastest = list(inputs_angles)
            if f < best_time:
                closest = -1
                best_time = f
                frame_data_earliest = list(inputs_angles)
            
            if target[1] < init_state.pos_y: # target is above us
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
            if abs(state.pos_y - target[1]) < closest:
                closest = abs(state.pos_y - target[1])

            if state.pos_y > target[1]:
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
            
            if abs(state.pos_y - target[1]) == last_diff:
                break

            last_diff = abs(state.pos_y - target[1])
            
        options += 1
        state.reset_state()

    logging.info(f"Done, tried {options} ratios")
    return frame_data_fastest, frame_data_earliest


def method_manual_wiggle(init_state:State, frames: int, wiggle_horizontal: int, wiggle_vertical: int, wiggle_offset: int) -> list[float]:
    logging.info("Running manual wiggle method")
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

    state = init_state.clone_state()

    frame_data = []
    for f in range(frames):
        angle_hold = 0
        if wiggling:
            angle_hold = 90.0 if init_state.facing == Facings.Right else 270.0
        else:
            angle_hold = optimizer.find_best_vertical_input(state.angle, state.speed, state.facing)

        frame_data.append(angle_hold)
        state.step(angle_hold)

        wiggle_countdown -= 1
        if wiggle_countdown == 0:
            wiggling = not wiggling
            if wiggling:
                wiggle_countdown = wiggle_horizontal
            else:
                wiggle_countdown = wiggle_vertical

    return frame_data

def method_agent(init_state:State, frames:int, target:list[float], agent_amount:int, epochs:int, keep_top:int, mutation_rate:int, learning_rate:int, speed_multiplier:float, dist_multiplier:float, time_multiplier:float) -> list[float]:
    """Uses C++ and runs an agent method."""
    result = agent_module.train(agent_amount, epochs, mutation_rate, learning_rate, *init_state.init_state, *target, speed_multiplier, dist_multiplier, time_multiplier, keep_top)
    logging.debug(f"Result timings: {result}")

    state = init_state.clone_state()
    frame_data = []
    for i, t in enumerate(result):
        for _ in range(t):
            if i % 2 == 1:
                    angle = optimizer.find_best_vertical_input(state.angle, state.speed, state.facing)
                    state.step(angle)
                    frame_data.append(angle)
            else:
                angle = 90.0 if state.facing == Facings.Right else 270.0
                state.step(angle)
                frame_data.append(angle)

            # logging.debug(f"Python simulated Agent with new pos=[{state.pos_x}, {state.pos_y}], speed={state.speed}")
            if state.pos_x * state.facing.value >= target[0] * state.facing.value:
                break

        if state.pos_x * state.facing.value >= target[0] * state.facing.value:
                break
    
    logging.info(f"Predicted arrival: Pos={state.pos_x}, {state.pos_y} / Speed={state.speed} / Arrival in {len(frame_data)}f")
    logging.debug(f"Percentage of flight path used: {((i+1)/len(result))*100}%.")

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
        logging.info("Running default window setup")
        method: ttk.Combobox = self.builder.get_object('method')
        method.current(0)

        mj_method: ttk.Combobox = self.builder.get_object('mj_method')
        mj_method.current(0)

    def run(self):
        # check if first time running
        first_launch = not os.path.exists("./firstlaunch")
        if first_launch:
            logging.info("Detected first launch")
            open("./firstlaunch", "w").close()
            self.mainwindow.after(0, self.info)
        self.mainwindow.mainloop()

    def optimize(self):
        method: ttk.Combobox = self.builder.get_object('method')
        active_method = method.current()
        self.last_method = active_method
        logging.info(f"Optimizer launched on method {active_method}")

        gamestate_box: tk.Entry = self.builder.get_object("gamestate")

        frame_count = self.builder.get_variable("frames").get()

        target = [
            self.builder.get_variable("target_x").get(),
            self.builder.get_variable("target_y").get()
        ]

        hotkey = self.builder.get_variable("hotkey").get()
        try:
            gamestate_data = State(gamestate_box.get("1.0", "end"))
        except ValueError as e:
            logging.error(f"Couldn't load state: State text is missing required information")
            return
        except Exception as e:
            logging.error(f"Couldn't load state: '{e}'")
        
        logging.info("Loaded state successfully")

        # get manual wiggle data
        wiggle_horizontal = self.builder.get_variable("wiggle_horizontal").get()
        wiggle_vertical = self.builder.get_variable("wiggle_vertical").get()
        wiggle_offset = self.builder.get_variable("wiggle_offset").get()

        if active_method == 0:  # normal pullup
            frame_data = method_normal_pullup(gamestate_data, frame_count)
            self.set_output_text(optimizer.frameDataToInputs(frame_data, hotkey))

        elif active_method == 1:  # megajoule method
            mj_selection: ttk.Combobox = self.builder.get_object('mj_method')
            self.input_data_mj[0], self.input_data_mj[1] = method_megajoule(gamestate_data, frame_count, target)
            # mj might not arrive at the target
            # need to account for that
            # if it doesn't, then both input_data_mj[0] and [1] will be empty
            if len(self.input_data_mj[0]) == 0:
                self.set_output_text(self.couldnt_path_msg)
                return
            
            self.set_output_text(optimizer.frameDataToInputs(self.input_data_mj[mj_selection.current()], hotkey))

        elif active_method == 2:  # manual wiggle
            frame_data = method_manual_wiggle(gamestate_data, frame_count, wiggle_horizontal, wiggle_vertical, wiggle_offset)
            self.set_output_text(optimizer.frameDataToInputs(frame_data, hotkey))
        
        elif active_method == 3: # agent method
            # fetch all the variables
            agent_amount = self.builder.get_variable("agent_amount").get()
            epochs = self.builder.get_variable("epoch_amount").get()
            keep = self.builder.get_variable("keep_top").get()
            mutation_rate = self.builder.get_variable("mutation_rate").get()
            learning_rate = self.builder.get_variable("learning_rate").get()
            speed_multiplier = self.builder.get_variable("speed_multiplier").get()
            dist_multiplier = self.builder.get_variable("dist_multiplier").get()
            time_multiplier = self.builder.get_variable("time_multiplier").get()

            # since learning rate is a percent
            learning_rate = int((learning_rate / 100) * 250)

            start = time.time()
            frame_data = method_agent(gamestate_data, frame_count, target, agent_amount, epochs, keep, mutation_rate, learning_rate, speed_multiplier, dist_multiplier, time_multiplier)
            end = time.time()
            
            logging.info(f"Completed in {end-start:.2f}s")
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
    
    def info(self, file:str):
        """Opens a file and displays it as an info box. The first line of that file will be used as the window title."""
        with open(file, "r", encoding="utf-8") as infobox:
            contents = infobox.read().splitlines()
            title = contents[0]
            text = "\n".join(contents[1:])
        messagebox.showinfo(title, text)

    def how_to_use(self):
        self.info("infobox.txt")
    
    def agent_info(self):
        self.info("agent_options.txt")
    
    def doc_clipboard(self):
        webbrowser.open_new("https://docs.google.com/document/d/1xFF6wjdig5k9vOUF3mAvvWh4pF2HBvOw5PJ-aCNNeTo")


if __name__ == "__main__":
    setup_logging()
    try:
        app = Glideline()
        app.run()
    except Exception as e:
        logging.critical(f"Uncaught exception: {e}\nTraceback: {e.__traceback__}")
        quit()