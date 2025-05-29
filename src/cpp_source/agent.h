#pragma once

#include <vector>
#include "elytrastate.h"

class Agent
{
    public:
        std::vector<int> timings;
        ElytraState state;
        double get_next_input();
        bool has_next_input();
        void res();

        Agent(ElytraState init_state);
        // ~Agent();

        Agent *clone_agent();
        void mutate_pullup(int max_amount, int timing_amount);
        void mutate_levelout(int max_amount, int timing_amount);
        void mutate_all(int max_amount, int timing_amount);
        
        private:
        void mutate(int max_amount, int timing_amount, int lr);
        Agent(); // this one is private for cloning purposes and will do nothing
        static constexpr int timings_max_size = 250;
        int timings_i;
        int input_i;
};