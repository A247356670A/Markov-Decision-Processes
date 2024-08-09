from MDP import MDP
from dungeon import basic_map, DungeonMDP
from modelling import *
from algos import value_iteration

map = basic_map()
dg = DungeonMDP(map)
limit = 10



Q3_answer = 40
while True:
    modifiedMDP01 = limit_action_number(dg, q3_action_condition, limit)
    pi01,value01 = value_iteration(modifiedMDP01, gamma=GAMMA, epsilon=EPSILON)
    print(f'Value in the initial state: {value01.value(modifiedMDP01.initial_state())}')
    if value01.value(modifiedMDP01.initial_state()) >= 30 and value01.value(modifiedMDP01.initial_state()) <= 40:
        print("found!")
        print(Q3_answer)
        break
    Q3_answer += 1