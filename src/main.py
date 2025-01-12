import tkinter as tk
import clipboard
from optimizer import *
from simulator import *

class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.title("Glideline")
        self.geometry("600x400")

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)

        # Add widgets
        self.create_widgets()

    def create_widgets(self):
        self.game_state = tk.Text(self, height=10, width=20)
        self.game_state.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # self.Leftlabel = tk.Label(self, text="Enter Game state here", font=("Arial", 12))
        # self.Leftlabel.grid(row=0, column=0)


        # Middle section with a button and a label
        self.middle_button = tk.Button(self, text="Run optimizer ->", command=self.run_optimizer)
        self.middle_button.grid(row=0, column=1, padx=10, pady=10)

        # Text box on the right
        self.output_box = tk.Text(self, height=10, width=20)
        self.output_box.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        self.copy_button = tk.Button(self, text="Copy output", command=self.copy_output)
        self.copy_button.grid(row=1, column=2)
    
    def copy_output(self):
        clipboard.copy(self.output_box.get("1.0", "end").rstrip())
    
    def run_optimizer(self):
        # grab the game state
        data = self.game_state.get("1.0", "end").rstrip().splitlines()
        speedIndex = [1 if x.startswith("Speed") else 0 for x in data].index(1)
        speedString = data[speedIndex][len("Speed: "):]
        speedX = float(speedString.split(", ")[0])
        speedY = float(speedString.split(", ")[1])
        facing = Facings.Left if speedX < 0 else Facings.Right # flip the x speed if facing left

        current_speed = sqrt((speedX**2) + (speedY**2))
        current_angle = (((atan2(speedY, speedX * facing.value) * RAD_TO_DEG) + 90) + 360) % 360

        out_data = []
        for i in range(100):
            angle_hold = find_best_vertical_input(current_angle, current_speed, facing)
            current_speed, current_angle = simulate(current_speed, current_angle, angle_hold)
            out_data.append(angle_hold)
        
        self.output_box.delete("1.0", "end")
        self.output_box.insert("1.0", frameDataToInputs(out_data))



if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
