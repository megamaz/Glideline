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

class Tool:
    def __init__(self):
        # keep track of the player state
        self.init_target = [0, 0]
        self.init_pos = [0, 0]
        self.init_speed = 0
        self.init_angle = 0
        self.init_spinners = []

        # to interact with the cli
        self.COMMANDS = {
            "help":self.print_help,
            "target":self.set_target,
            "gamestate":self.set_gamestate,
            "finish":"Ends the program."
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
            command_list = list(self.COMMANDS.keys())
            command_list.sort()
            print(f"Available commands are: {', '.join(command_list)}\ndo `help [command]` to get more help on a specific command.")
            return


    def set_target(self, *args):
        """Sets the position of the next target to optimize to."""
        print("Enter target positions.")
        self.init_target[0] = float(input(" X: "))
        self.init_target[1] = -float(input(" Y: "))
    
    def set_gamestate(self, *args):
        """Sets the current gamestate. Copy from Studio, and paste it into here."""
        print("Paste in gamestate. Enter `DONE` in all caps when done.")
        gamestate = accept_multiline_input().splitlines()
        pos_index = [1 if x.startswith("Pos") else 0 for x in gamestate].index(1)
        speed_index = [1 if x.startswith("Speed") else 0 for x in gamestate].index(1)


if __name__ == "__main__":
    t = Tool()
    t.cli_loop()