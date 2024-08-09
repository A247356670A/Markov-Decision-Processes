from MDP import MDP
from dungeon import basic_map, DungeonMDP
from modelling import *
from algos import value_iteration

map = basic_map()
dg = DungeonMDP(map)

modifiedMDP01 = forbid_actions_in_states(dg, q2_action_condition1, q2_state_condition1)
pi01,value01 = value_iteration(modifiedMDP01, gamma=GAMMA, epsilon=EPSILON)
print(f'Value in the initial state: {value01.value(modifiedMDP01.initial_state())}')

modifiedMDP02 = forbid_actions_in_states(dg, q2_action_condition2, q2_state_condition2)
pi02,value02 = value_iteration(modifiedMDP02, gamma=GAMMA, epsilon=EPSILON)
print(f'Value in the initial state: {value02.value(modifiedMDP02.initial_state())}')

