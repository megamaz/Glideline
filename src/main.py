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



if __name__ == "__main__":
    ...