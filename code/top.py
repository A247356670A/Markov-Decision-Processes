from typing import Set, List, Tuple, Optional
from algos import StateValueFunction, ActionValueFunction, one_step_lookahead, greedy_action, compute_q_from_v, \
    greedy_policy, value_iteration, state_value_difference
from MDP import State, MDP, Policy, ExplicitPolicy
from connectedcomp import CCGraph


def topological_vi(mdp: MDP, gamma: float, epsilon: float, graph: CCGraph) -> StateValueFunction:
    # print(mdp.states())
    # print(mdp.actions())
    # print(graph.print())
    # print("----")
    ccDic = dict()
    ccSet = set(graph.roots())
    continueFlag = True
    dic = 0
    while continueFlag:
        for each in ccSet:
            # print(each.states())
            ccDic[dic] = each.states()
            dic += 1
            if each.children():
                ccSet = each.children()
            else:
                continueFlag = False

    # print(ccDic)
    v = StateValueFunction()
    # polC, vC = value_iteration(mdp, gamma, epsilon)
    statesList = []
    for key in reversed(ccDic.keys()):
        innerCCs = ccDic[key]
        for each in innerCCs:
            statesList.append(each)
        # print(innerCCs)
        pol, v = value_iteration_states(mdp, gamma, epsilon, statesList, v)
        # for s in mdp.states():
            # print("v.value(s): ",s,": ", v.value(s))
            # print("answer: ",s,": ", vC.value(s))
            # print("-------")

    return v


# eof
def compute_q_from_v_states(mdp: MDP, v: StateValueFunction, gamma: float, states: List[State]) -> ActionValueFunction:

    result = ActionValueFunction()
    for s in states:
        for a in mdp.applicable_actions(s):
            result.set_value(s, a, one_step_lookahead(mdp, v, gamma, s, a))
    return result


def greedy_policy_states(mdp: MDP, q: ActionValueFunction, states: List[State]) -> Tuple[Policy, StateValueFunction]:

    result_pol = ExplicitPolicy(mdp)
    result_val = StateValueFunction()
    for s in states:
        action, val = greedy_action(mdp, q, s)
        result_pol.set_action(s, action)
        result_val.set_value(s, val)
    return result_pol, result_val


NB_BACKUPS = 0


def bellman_backup_states(mdp: MDP, v: StateValueFunction, gamma: float, states: List[State]) -> Tuple[
    Policy, StateValueFunction]:

    global NB_BACKUPS
    q = compute_q_from_v_states(mdp, v, gamma, states)
    NB_BACKUPS += 1
    return greedy_policy_states(mdp, q, states)


def value_iteration_states(mdp: MDP, gamma: float, epsilon: float, states: List[State],
                           starting_value: StateValueFunction) -> Tuple[
    Policy, StateValueFunction]:

    vs = starting_value
    while True:
        pol, newvs = bellman_backup_states(mdp, vs, gamma, states)
        diff = state_value_difference(mdp, vs, newvs)
        if diff < epsilon:
            return pol, newvs
        vs = newvs
