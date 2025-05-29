#include "elytrastate.h"
#include "simulator.h"
#include "constants.h"
#include <cmath>
#include <array>

ElytraState::ElytraState()
{
    this->pos_x = 0;
    this->pos_y = 0;
    this->speed = 0;
    this->angle = 0;
    this->facing = 0;
    this->init_pos_x = 0;
    this->init_pos_y = 0;
    this->init_speed = 0;
    this->init_angle = 0;
    this->init_facing = 0;
}

ElytraState::ElytraState(double pos_x, double pos_y, double speed, double angle, double wind_x, double wind_y, int facing)
{
    this->pos_x = pos_x;
    this->pos_y = pos_y;
    this->wind_x = wind_x;
    this->wind_y = wind_y;
    this->speed = speed;
    this->angle = angle;
    this->facing = facing;

    this->init_pos_x = pos_x;
    this->init_pos_y = pos_y;
    this->init_wind_x = wind_x;
    this->init_wind_y = wind_y;
    this->init_speed = speed;
    this->init_angle = angle;
    this->init_facing = facing;
    
}

void ElytraState::reset_state()
{
    this->pos_x = this->init_pos_x;
    this->pos_y = this->init_pos_y;
    this->speed = this->init_speed;
    this->angle = this->init_angle;
    this->facing = this->init_facing;
}

ElytraState::ElytraState(const ElytraState& other)
{
    pos_x = other.pos_x;
    pos_y = other.pos_y;
    speed = other.speed;
    angle = other.angle;
    facing = other.facing;

    init_pos_x = other.init_pos_x;
    init_pos_y = other.init_pos_y;
    init_speed = other.init_speed;
    init_angle = other.init_angle;
    init_facing = other.init_facing;
}

ElytraState* ElytraState::clone_state()
{
    return new ElytraState(*this);
}

void ElytraState::step(double i)
{
    std::array<double, 2> result = Simulator::simulate(this->angle, this->speed, i);
    this->angle = result[0];
    this->speed = result[1];

    this->pos_x += (this->speed * std::sin(this->angle * deg_to_rad) + this->wind_x) * delta_time * this->facing;
    this->pos_y -= (this->speed * std::cos(this->angle * deg_to_rad) + this->wind_y) * delta_time;
}