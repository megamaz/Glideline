#pragma once

#include <limits>
#include "constants.h"
#include <algorithm>

inline double inf = std::numeric_limits<double>::infinity();

inline double max_angle_change_formula(double speed)
{
    if (speed == 0.0)
        return inf;
    return delta_time * max_angle_change_inv_speed_factor / speed;
}

inline double approach(double value, double target, double step)
{
    if (value > target)
        return std::max(value - step, target);
    else if (value < target)
        return std::min(value + step, target);

    return target;
}

inline double clamp(double value, double min_value, double max_value)
{
    return std::min(std::max(value, min_value), max_value);
}