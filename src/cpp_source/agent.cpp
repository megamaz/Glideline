#include "agent.h"
#include "simulator.h"
#include "optimizer.h"
#include <algorithm>
#include <random>
#include <iostream>

Agent::Agent(ElytraState init_state)
{
    this->state = init_state;
    
    this->timings.assign(timings_max_size, 5);
    // std::random_device rd;
    // std::mt19937 gen(rd());
    // std::uniform_int_distribution<> dist(3, 6);
    // for (int i = 0; i < timings_max_size; i++)
    // {
    //     this->timings[i] = dist(gen);
    // }
}

// blank constructor for cloning purposes
Agent::Agent() : state(ElytraState(0, 0, 0, 0, 0, 0, 1)){}

double Agent::get_next_input()
{
    double angle = 0.0;
    if (timings_i % 2 == 0)
        angle = this->state.facing == -1 ? 270.0 : 90.0;
    else
        angle = Optimizer::find_best_vertical_input(this->state.angle, this->state.speed, this->state.facing);
    

    this->input_i++;
    if(this->input_i == this->timings[this->timings_i])
    {
        this->input_i = 0;
        this->timings_i++;
    }

    return angle;
}

bool Agent::has_next_input()
{
    return this->timings_i < timings_max_size && this->input_i < this->timings[this->timings_i];
}

void Agent::res()
{ 
    this->timings_i = 0;
    this->input_i = 0;
}

// clone
Agent *Agent::clone_agent()
{
    Agent *new_agent = new Agent();
    new_agent->timings.assign(timings_max_size, -1); // this will get overwritten anyways
    for (int i = 0; i < timings_max_size; i++)
    {
        new_agent->timings[i] = this->timings[i];
    }
    new_agent->state = *(this->state.clone_state());
    new_agent->timings_i = 0;
    new_agent->input_i = 0;

    return new_agent;
}

void Agent::mutate_pullup(int max_amount, int timing_amount)
{
    this->mutate(max_amount, timing_amount, 1);
}

void Agent::mutate_levelout(int max_amount, int timing_amount)
{
    this->mutate(max_amount, timing_amount, 0);
}

void Agent::mutate_all(int max_amount, int timing_amount)
{
    this->mutate(max_amount, timing_amount, -1);
    this->mutate(-max_amount, timing_amount, -1);
}

void Agent::mutate(int max_amount, int timing_amount, int lr)
{
    std::random_device rd;
    std::mt19937 gen(rd());

    int min_range = std::min(0, max_amount);
    int max_range = std::max(0, max_amount);

    std::uniform_int_distribution<> dist(min_range, max_range);
    if (timing_amount == -1)
    {
        for (int i = 0; i < timings_max_size; i++)
        {
            if (i % 2 == lr || lr == -1)
                this->timings[i] = std::max(0, this->timings[i] + dist(gen));
        }
    }
    else
    {
        std::vector<int> indices;
        for (int i = 0; i < timings_max_size; ++i)
        {
            if (i % 2 == lr || lr == -1)
                indices.push_back(i);
        }
        std::shuffle(indices.begin(), indices.end(), gen);
        for (int x = 0; x < timing_amount; ++x)
        {
            int idx = indices[x];
            this->timings[idx] = std::max(0, this->timings[idx] + dist(gen));
        }
    }
}

// Agent::~Agent()
// {
//     delete &state;
// }