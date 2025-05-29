#include "constants.h"
#include "optimizer.h"
#include "utilities.h"
#include "simulator.h"
#include <cmath>
#include <iostream>
#include <array>

double Optimizer::find_best_vertical_input(double initial_angle, double initial_speed, int facing)
{
    const double maxAngleChange = delta_time * max_angle_change_inv_speed_factor / initial_speed;
    double angle_min = 0.0;
    // if we're moving "down" but above the stable angle
    // then we don't want to optimize for immediate height
    if (initial_angle > 90.0 && initial_angle < 90.0 + stable_angle_deg) {
        angle_min = std::acos((stable_angle - (((initial_angle - 90.0) * pi) / 180.0))) * rad_to_deg - (maxAngleChange * rad_to_deg);
    }
    double angle_max = 180.0;

    double init_min_angle = angle_min;
    double init_max_angle = angle_max;

    double best_yspeed = inf;
    double best_total_speed = inf;
    double best_angleI = 0.0;
    double best_angleF = 0.0;
    double step_size = 1.0;
    int iteration = 1;

    bool end_prematurely = false;
    while (iteration < 12) {
        for (double angle = angle_min; angle < angle_max; angle += step_size) {
            double test_angle = angle;
            if (initial_angle < 180.0) {
                test_angle = angle_max - test_angle + angle_min;
            }
            // simulate in-game speed changes
            double new_angle, new_speed;
            std::array<double, 2> result = Simulator::simulate(initial_angle, initial_speed, test_angle);
            new_angle = result[0];
            new_speed = result[1];
            double ySpeed = new_speed * -std::sin((90.0 - new_angle) * deg_to_rad);
            // if we're flying down then we want to optimize for long-term speed
            if (initial_angle > 90.0 + stable_angle_deg && initial_speed <= max_speed) {
                test_angle = 0.0;
                end_prematurely = true;
            }

            // since y speed is negative when moving up
            if (ySpeed < best_yspeed) {
                best_yspeed = ySpeed;
                best_total_speed = new_speed;
                best_angleI = test_angle;
                best_angleF = new_angle;
            }

            if (end_prematurely) {
                break;
            }
        }

        // once we've found our best angle for this frame, narrow down precision
        angle_min = best_angleI - 10.0 / std::pow(10.0, iteration);
        angle_max = best_angleI + 10.0 / std::pow(10.0, iteration);

        // prevent angles from exiting the bounds of their initial values
        angle_min = std::max(init_min_angle, angle_min);
        best_angleI = std::max(init_min_angle, best_angleI);
        angle_max = std::min(init_max_angle, angle_max);
        best_angleI = std::min(init_max_angle, best_angleI);

        step_size /= 10.0;
        iteration ++;
    }

    initial_angle = best_angleF;
    initial_speed = best_total_speed;

    double angle_hold = best_angleI;
    if (facing == -1) {
        angle_hold = std::fmod(-best_angleI, 360.0);
        if (angle_hold < 0) angle_hold += 360.0;
    }

    return angle_hold;
}