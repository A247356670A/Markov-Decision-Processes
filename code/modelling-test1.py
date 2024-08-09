from MDP import MDP
from dungeon import basic_map, DungeonMDP
from modelling import *
from algos import value_iteration

map = basic_map()
dg = DungeonMDP(map)

Q1_answer = 45
while True:
    modifiedMDP01 = penalise_state_action(dg, q1_action_condition, q1_state_condition, Q1_answer)
    pi01,value01 = value_iteration(modifiedMDP01, gamma=GAMMA, epsilon=EPSILON)
    print(f'Value in the initial state: {value01.value(modifiedMDP01.initial_state())}')
    if value01.value(modifiedMDP01.initial_state()) >= 30 and value01.value(modifiedMDP01.initial_state()) <= 40:
        print("found!")
        print(Q1_answer)
        break
    Q1_answer += 1