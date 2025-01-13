import clipboard
from optimizer import *
from simulator import *

def accept_multiline_input(terminator:str="DONE") -> str:
    all_lines = []
    while True:
        data = input("... ")
        if data != terminator:
            all_lines.append(data)
        else:
            break
    return "\n".join(all_lines)

class Gamestate:
    # keeps track of the gamestate
    def __init__(self):
        self.pos = [0, 0]
        self.speed = 0
        self.angle = 0

class Tool:
    def __init__(self):
        self.state = Gamestate()
        self.target = [0, 0]
        self.spinners = []

        # to interact with the cli
        self.COMMANDS = {
            "help":self.print_help,
            "target":self.set_target,
            "gamestate":self.set_gamestate,
            "settings":self.set_settings,
            "finish":"Ends the program.",
        }

        # settings
        self.settings = {
            "elytra_hotkey":"PE"
        }

    def cli_loop(self):
        print("Welcome to Glideline, a CLI tool for optimizing elytra movement. Commands are case sensitive. run `help` for a list of commands.\n\nNote: it was originally planned to be a tkinter window. If you have experience with tkinter windows or other gui features, please feel free to PR the Glideline repository: https://github.com/megamaz/Glideline")
        while True:
            command_line = input(">>> ")
            command = command_line.split(" ")[0]
            if self.COMMANDS.get(command):
                # manual implementations
                if command == "finish":
                    print("cya later")
                    break
                
                # function implementations
                params = []
                if len(command_line.split(" ")) > 1:
                    params = command_line.split(" ")[1:]

                try:
                    self.COMMANDS[command](*params)
                except Exception as e:
                    print(f"Error occured when running command {command}: {e}")
            else:
                print(f"Unrecognized command `{command}`. Commands are case-sensitive. Run `help` for a list of commands.")
    
    def print_help(self, command:str=None, *args):
        """Gives help on given commands. Seems like you know how to use it."""
        if command:
            if self.COMMANDS.get(command):
                if type(self.COMMANDS[command]) == str:
                    print(self.COMMANDS[command])
                    return
                print(self.COMMANDS[command].__doc__)
            else:
                print(f"Function {command} does not exist")
        else:
            command_list = list(self.COMMANDS.keys())
            command_list.sort()
            print(f"Available commands are: {', '.join(command_list)}\ndo `help [command]` to get more help on a specific command.")
            return


    def set_target(self, *args):
        """Sets the position of the next target to optimize to."""
        print("Enter target positions.")
        self.target[0] = float(input(" X: "))
        self.target[1] = float(input(" Y: "))
    
    def set_gamestate(self, *args):
        """Sets the current gamestate. Copy directly from Studio. Allows spinner entity watch info to be selected."""
        print("Paste in gamestate. Enter `DONE` in all caps when done.")
        gamestate = accept_multiline_input().splitlines()
        pos_index = [1 if x.startswith("Pos") else 0 for x in gamestate].index(1)
        speed_index = [1 if x.startswith("Speed") else 0 for x in gamestate].index(1)

        self.state.pos = [
            float(gamestate[pos_index][len("Pos: "):].split(", ")[0]), float(gamestate[pos_index].split(", ")[1])
        ]
        speedString = gamestate[speed_index][len("Speed: "):]
        speedX = float(speedString.split(", ")[0])
        speedY = float(speedString.split(", ")[1])
        facing = Facings.Left if speedX < 0 else Facings.Right # flip the x speed if facing left
        self.state.speed = sqrt((speedX**2) + (speedY**2))
        self.state.angle = (((atan2(speedY, speedX * facing.value) * RAD_TO_DEG) + 90) + 360) % 360
    
    def set_settings(self, *args):
        """Changes the settings of Glideline. All settings are reset to default on launch."""
        for a in args:
            ...



if __name__ == "__main__":
    t = Tool()
    t.cli_loop()