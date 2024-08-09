from MDP import MDP
from dungeon import basic_map, DungeonMDP
from modelling import *
from algos import value_iteration

map = basic_map()
dg = DungeonMDP(map)

modifiedMDP00 = add_cost_to_actions(dg, q0_action_condition, Q0_answer)
pi00,value00 = value_iteration(modifiedMDP00, gamma=GAMMA, epsilon=EPSILON)
print(f'Value in the initial state: {value00.value(modifiedMDP00.initial_state())}')
