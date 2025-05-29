#pragma once

#include "elytrastate.h"
#include <array>

class Optimizer
{
    public:
        static double find_best_vertical_input(double init_angle, double init_speed, int facing);
};