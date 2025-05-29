#pragma once

#include <array>

class Simulator
{
    public:
        static std::array<double, 2> simulate(double init_angle, double init_speed, double input);
};