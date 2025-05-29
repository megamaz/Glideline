#include "simulator.h"
#include "utilities.h"
#include "constants.h"
#include <cmath>
#include <array>

std::array<double, 2> Simulator::simulate(double init_angle, double init_speed, double input)
{
    double max_angle_change = max_angle_change_formula(init_speed);
    double half_range = angle_range / 2.0;
    double new_speed = init_speed;
    double new_angle = init_angle;
    double yInput = -std::sin((input + 90.0) * deg_to_rad);

    // simulate elytra code
    // angle
    if (init_speed == min_speed && yInput < 0)
        new_angle = approach(init_angle, (stable_angle * rad_to_deg) + 90.0, max_angle_change * rad_to_deg);
    else
    {
        double target = ((stable_angle + half_range * yInput) * rad_to_deg) + 90.0;
        new_angle = approach(init_angle, target, max_angle_change * rad_to_deg);
    }
    new_angle = clamp(new_angle, ((stable_angle - half_range) * rad_to_deg) + 90.0, ((stable_angle + half_range) * rad_to_deg) + 90.0);

    // speed
    if (std::sin((new_angle - 90.0) * deg_to_rad) < std::sin(stable_angle))
    {
        double decel_now = init_speed > max_speed ? fast_decel : decel;
        new_speed = approach(init_speed, min_speed, delta_time * decel_now * std::abs(yInput));
    }
    else
    {
        if(init_speed < max_speed)
            new_speed = approach(init_speed, max_speed, delta_time * accel * std::abs(yInput));
    }

    return {new_angle, new_speed};
}