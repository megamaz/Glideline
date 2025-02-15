from constants import *
from math import atan2, sqrt
import simulator

class ElytraState:
    pos:list[float]
    speed:float
    angle:float
    facing:Facings
    
    selected_spinners:list

    def __init__(self, state_str:str):
        speedIndex = [1 if x.startswith(
        "Speed") else 0 for x in state_str].index(1)
        speedString = state_str[speedIndex][len("Speed: "):]
        speedX = float(speedString.split(", ")[0])
        speedY = float(speedString.split(", ")[1])
        self.facing = Facings.Left if speedX < 0 else Facings.Right
        self.speed = sqrt((speedX**2), (speedY**2))

        self.angle = (((atan2(speedY, speedX * self.facing.value) * RAD_TO_DEG) + 90) + 360) % 360

        posIndex = [1 if x.startswith(
        "Pos") else 0 for x in state_str].index(1)
        posString = state_str[posIndex][len("Pos: "):]
        self.pos = [
            float(posString.split(", ")[0]),
            float(posString.split(", ")[1])
        ]
        
    def step(self, input_angle:float):
        self.angle, self.speed = simulator.simulate(self.angle, self.speed, input_angle)