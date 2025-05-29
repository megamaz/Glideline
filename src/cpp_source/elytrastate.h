#pragma once

#include <string>

class ElytraState
{
    public:
        double pos_x;
        double pos_y;
        double wind_x;
        double wind_y;
        double speed;
        double angle;
        int facing;

        ElytraState();
        ElytraState(double pos_x, double pos_y, double speed, double angle, double wind_x, double wind_y, int facing);
        ElytraState(std::string state_str);
        ElytraState(const ElytraState &other);
        void reset_state();
        void step(double i);
        ElytraState *clone_state();

    private:
        double init_pos_x;
        double init_pos_y;
        double init_wind_x;
        double init_wind_y;
        double init_speed;
        double init_angle;
        int init_facing;
};