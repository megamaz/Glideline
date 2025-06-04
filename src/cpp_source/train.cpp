#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "agent.h"
#include "elytrastate.h"
#include <random>
#include <iostream>
#include "utilities.h"

pybind11::object logger;

void setup_logger(pybind11::object l)
{
    logger = l;
    logger.attr("info")("Logger setup in C++");
}

// returns a vector of the timings of the best agent
std::vector<int> train(int agent_amount, int epochs, int mutate_rate, int learning_rate, double pos_x, double pos_y, double speed, double angle, double wind_x, double wind_y, int facing, double target_x, double target_y, double speed_multiplier, double distance_multiplier, double frames_multiplier, int keep_top)
{
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dist(0, 1);

    ElytraState *init_state = new ElytraState(pos_x, pos_y, speed, angle, wind_x, wind_y, facing);
    std::vector<Agent*> agents;
    double *agent_scores = new double[agent_amount];
    // 0.0 means initialized
    // -inf means didn't arrive
    // -2.0 means unsimulated

    std::vector<double> target = {target_x, target_y};
    for (int i = 0; i < agent_amount; i++)
    {
        ElytraState* cloned_state = init_state->clone_state();
        Agent *new_agent = new Agent(*cloned_state);
        agents.push_back(new_agent);
        agent_scores[i] = 0.0; 
        delete cloned_state;
    }

    bool fine_tuning = false;
    for (int e = 0; e < epochs; e++)
    {
        // std::cout << "\rSimulating and scoring agents for epoch " << e+1 << "/" << epochs << " (" << ((float)(e+1)/(float)(epochs))*100.0f << "%)" << std::flush;
        for (int a = 0; a < agent_amount; a++)
        {
            Agent* agent = agents[a];
            // reset input stuff
            // std::cout << "Simulating Agent# " << a+1 << " with timing values " << std::endl;
            // for (int i = 0; i < 250; i++)
            // {
            //     std::cout << agent->timings[i] << ", ";
            // }
            // std::cout << std::endl;

            agent->res();
            int frames = 0;
            while (agent->has_next_input())
            {
                double input = agent->get_next_input();
                agent->state.step(input);
                // std::cout << "new pos_x=" + std::to_string(agent->state.pos_x) + " pos_y=" + std::to_string(agent->state.pos_y) + " speed=" + std::to_string(agent->state.speed) + " angle=" + std::to_string(agent->state.angle) << std::endl;
                // logger.attr("debug")("Agent #" + std::to_string(a + 1) + " new pos_x=" + std::to_string(agent->state.pos_x) + " pos_y=" + std::to_string(agent->state.pos_y) + " speed=" + std::to_string(agent->state.speed) + " angle=" + std::to_string(agent->state.angle) + " input=" + std::to_string(input));
                if (agent->state.pos_x * agent->state.facing >= target[0] * agent->state.facing)
                {
                    double score = (agent->state.speed * speed_multiplier) + (std::abs(agent->state.pos_y - target[1]) * distance_multiplier) + (frames * frames_multiplier);
                    agent_scores[a] = score;
                    break;
                }
                frames++;
            }
            if (agent->state.pos_x * agent->state.facing < target[0] * agent->state.facing)
            {
                agent_scores[a] = -inf;
            }
            // std::cout << "Agent #" << a + 1 << " finished at [" << agent->state.pos_x << ", " << agent->state.pos_y << "] speed=" << agent->state.speed << " with score=" << agent_scores[a] << std::endl;
            // logger.attr("debug")("Agent #" + std::to_string(a + 1) + " finished at [" + std::to_string(agent->state.pos_x) + ", " + std::to_string(agent->state.pos_y) + "] speed=" + std::to_string(agent->state.speed) + " with score=" + std::to_string(agent_scores[a]));
        }

        // sort agents
        std::vector<std::pair<double, Agent*>> score_agent_pairs;
        for (int i = 0; i < agent_amount; ++i) {
            score_agent_pairs.emplace_back(agent_scores[i], agents[i]);
        }
        std::sort(score_agent_pairs.begin(), score_agent_pairs.end(),
                  [](const std::pair<double, Agent*>& a, const std::pair<double, Agent*>& b) {
                      return a.first > b.first; // Sort descending by score
                  });
        for (int i = 0; i < agent_amount; ++i) {
            agent_scores[i] = score_agent_pairs[i].first;
            agents[i] = score_agent_pairs[i].second;
            // std::cout << "agent #" + std::to_string(i+1) + "(pointer " << score_agent_pairs[i].second << ") score: " + std::to_string(score_agent_pairs[i].first) << std::endl;
        }
        logger.attr("info")("Best score of epoch " + std::to_string(e+1) + ": " + std::to_string(score_agent_pairs[0].first));
        // std::cout << "best agent timings: [";
        // for (int i = 0; i < 250; i++)
        // {
        //     std::cout << agents[0]->timings[i] << ", ";
        // }
        // std::cout << "]" << std::endl;

        // Do NOT delete agents here; just erase pointers, cleanup at the end
        agents.erase(agents.begin() + keep_top, agents.end());
    
        // generate new agents
        int n = 0;
        // std::cout << "Cloning and mutation" << std::endl;
        // if(((float)epochs) * 0.9 < ((float)e) * 0.9 && !fine_tuning) // if we're on last 10% of epochs, turn down mutation rate for fine-tuning
        // {
        //     mutate_rate /= 2;
        //     fine_tuning = true;
        // }
        while (agents.size() < (size_t)agent_amount)
        {
            Agent *agent = agents[n % agents.size()];
            if (std::abs(agent->state.pos_y - target[1]) < 10)
            {
                // std::cout << "Cloning agent: close arrival" << std::endl;
                // reset the state first to ensure that there's no weird shenanigans
                // agent->state.reset_state();

                Agent *new_agent = agent->clone_agent();
                new_agent->mutate_all(mutate_rate, learning_rate);
                agents.push_back(new_agent);
            }
            else
            {
                // std::cout << "Cloning agent: far arrival" << std::endl;
                // agent->state.reset_state();

                Agent *new_agent = agent->clone_agent();
                if (agent->state.pos_y < target[1]) // less than means above
                {
                    if(dist(gen) == 0)
                        new_agent->mutate_levelout(mutate_rate, learning_rate);
                    else
                        new_agent->mutate_pullup(-mutate_rate, learning_rate);
                }
                else
                {
                    if(dist(gen) == 0)
                        new_agent->mutate_levelout(-mutate_rate, learning_rate);
                    else
                        new_agent->mutate_pullup(mutate_rate, learning_rate);
                }
                // std::cout << "Appending to agents list" << std::endl;
                agents.push_back(new_agent);
            }

            n++;
        }
        // std::cout << "`agents` size=" + std::to_string(agents.size()) + " vs scores size=" + std::to_string(agent_amount) + " vs agent_amount (goal)=" + std::to_string(agent_amount) << std::endl;

        // reset all agents and scores
        for (int i = 0; i < agent_amount; i++)
        {
            agents[i]->state.reset_state();
            if(agents[i]->state.pos_x != pos_x || agents[i]->state.pos_y != pos_y || agents[i]->state.speed != speed || agents[i]->state.angle != angle)
            {
                // std::cout << "Warning: Agent #" << i + 1 << " got invalid reset state." << std::endl;
                logger.attr("warning")("Agent #" + std::to_string(i+1) + " got invalid reset state.");
            }
            agent_scores[i] = -2.0;
        }
    }

    // safely copy the timings
    std::vector<int> timings = agents[0]->timings;

    // Clean up memory for all agents
    for (size_t i = 0; i < agents.size(); ++i) {
        delete agents[i];
    }
    delete init_state;
    delete[] agent_scores;

    return timings;
}

namespace py = pybind11;

PYBIND11_MODULE(agent_module, m) {
    m.def("train", &train);
    m.def("setup_logger", &setup_logger);
}
