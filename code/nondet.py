import copy
from itertools import chain, combinations
from typing import Dict, Tuple, Optional

from MDP import Action, State, MDP, Policy
from algos import StateValueFunction, value_iteration, state_value_difference, ActionValueFunction, greedy_action, \
    compute_v_of_policy, compute_q_from_v, greedy_policy


class NDPolicy:
    def __init__(self, copy: Optional = None):
        '''
          If copy is not empty, this policy is a copy of the specified policy
        '''
        if copy == None:
            self._actions = {}
        else:
            self._actions = {
                s: set(acts) for s, acts in copy._actions.items()
            }

    def add(self, s, a):
        if not s in self._actions:
            self._actions[s] = set()
        self._actions[s].add(a)

    def add_nondet_policy(self, ndpol):
        for s, acts in ndpol.items():
            if not s in self._actions:
                self._actions[s] = set()
            for a in acts:
                self._actions[s].add(a)

    def add_det_policy(self, mdp, pol: Policy):
        for s in mdp.states():
            self.add(s, pol.action(s))

    def actions(self, s):
        return self._actions[s]


def compute_policy_value(mdp: MDP, ndpol: NDPolicy, gamma: float, epsilon: float,
                         max_iteration: int) -> StateValueFunction:
    current_svalue = StateValueFunction()
    while max_iteration > 0:
        qvalue = ND_compute_q_from_v(mdp, current_svalue, gamma)
        new_svalue = ND_compute_v_from_q_and_policy(mdp, ndpol, qvalue)
        diff = state_value_difference(mdp, current_svalue, new_svalue)
        if diff < epsilon:
            return new_svalue
        current_svalue = new_svalue
        max_iteration = max_iteration - 1


def compute_non_augmentable_policy(mdp: MDP, gamma: float, epsilon: float, subopt_epsilon: float,
                                   max_iteration: int) -> NDPolicy:
    ndpol = NDPolicy()
    poltoCompare, vivalue = value_iteration(mdp, gamma, epsilon)
    ndpol.add_det_policy(mdp,poltoCompare)
    isPolicyAllreadyFit = False
    while True:
        if isPolicyAllreadyFit:
            actionsPairs =[]
            for s in mdp.states():
                for a in mdp.applicable_actions(s):
                    if a not in ndpol.actions(s):
                        actionsPairs.append((s,a))
            resultList = []
            for sublist in list(chain.from_iterable(combinations(actionsPairs, r) for r in range(1, len(actionsPairs)+1))):
                tempPol = NDPolicy()
                for s in mdp.states():
                    for a in ndpol.actions(s):
                        tempPol.add(s,a)
                for pair in sublist:
                    s = pair[0]
                    a = pair[1]
                    tempPol.add(s,a)
                vpiTemp = compute_policy_value(mdp, tempPol, gamma, epsilon, max_iteration)
                if ND_is_policy_nearly_greedy(mdp, vpiTemp, vivalue, subopt_epsilon):
                    resultList.append(sublist)

            if len(resultList)>0:
                maxList = max(resultList, key = len)
                for pair in maxList:
                    ndpol.add(pair[0], pair[1])
                return ndpol

        else:
            vpi = compute_policy_value(mdp, ndpol, gamma, epsilon, max_iteration)
            qs = ND_compute_q_from_v(mdp, vpi, gamma)
            if ND_is_policy_nearly_greedy(mdp, vpi, vivalue, subopt_epsilon):
                isPolicyAllreadyFit = True
                continue
            ndpol, vpi = ND_greedy_policy(mdp, qs)


'''
  TODO: Explain here why the non-deterministic policy 
  represented on the figure is not conservative epsilon-optimal 
  according to the definition of Fard and Pineau 
  (between 200 and 500 characters):
  
  According to the definition of V∗M(s), V∗M(s4) = 0,  V∗M(s2) = 100, V∗M(s3) = 100
  for action a from s0 to s2, to make the policy conservative epsilon-optimal, it should satisfy rule 7 
  which is:
        R(s0, a) + γ * (T(s0,a,s2) * (1−ε) * V∗M(s2)) ≥ (1−ε) * V∗M(s0)  
        LHS = -10, + 0.99 * (1 * (1 - 0.5) * 100)
            = 39.5
        but RHS = (1 - 0.5) * 89.09 = 44.545
  we can see LHS < RHS so rule 7 doesn't hold.
  so this policy is not conservative epsilon-optimal 
'''



# eof
def ND_compute_q_from_v(mdp: MDP, v: StateValueFunction, gamma: float) -> ActionValueFunction:
    '''
      Computes the action value function as a one-step lookahead value of the specified state value function.
    '''
    result = ActionValueFunction()
    for s in mdp.states():
        for a in mdp.applicable_actions(s):
            result.set_value(s, a, ND_one_step_lookahead(mdp, v, gamma, s, a))
    return result


def ND_compute_v_from_q_and_policy(mdp: MDP, pol: NDPolicy, q: ActionValueFunction) -> StateValueFunction:
    '''
      Computes the state value function as a one-step lookahead value of the specified action value function
      for the given policy.
    '''
    result = StateValueFunction()
    for s in mdp.states():
        vals = None
        # print(pol.actions(s) == None)
        for a in pol.actions(s):
            # print(s, a)

            if vals is None:
                vals = q.value(s, a)
            if q.value(s, a) < vals:
                vals = q.value(s, a)
        result.set_value(s, vals)
    return result


def ND_one_step_lookahead(mdp: MDP, v: StateValueFunction, gamma: float, s: State, a: Action
                          ) -> float:
    '''
      Computes the one-step lookahead value for the specified pair state/action, given the specified state value function.
      The one-step lookahead is calculated by looking at all the possible states that can be reached from executing the action,
      and adding their expected outcomes.
    '''
    value = 0
    for outcome in mdp.next_states(s, a):
        value += outcome.prob * (outcome.reward + (gamma * v.value(outcome.state)))
    return value


def ND_greedy_policy(mdp: MDP, q: ActionValueFunction) -> Tuple[NDPolicy, StateValueFunction]:
    '''
      Computes the greedy policy associated with the specified action value function.
      It also returns the associated state value function.
    '''
    result_pol = NDPolicy()
    result_val = StateValueFunction()
    for s in mdp.states():
        actions, val = ND_greedy_action(mdp, q, s)
        # print(actions)
        # result_pol.set_action(s, action)
        result_pol.add(s, actions)
        result_val.set_value(s, val)

    return result_pol, result_val


def ND_is_policy_nearly_greedy(mdp: MDP, Vndpol: StateValueFunction, Vpol: StateValueFunction, subopt_epsilon: float):
    '''
      Indicates whether the specified policy is nearly greedy for the action value function,
      i.e., whether the action it selects in each state has a value
      that is at most epsilon away from the value of the state with maximal value.
    '''
    for s in mdp.states():
        # print("s: ",s )
        # print("Vndpol.value(s): ", Vndpol.value(s))
        # print("(1 - subopt_epsilon) * Vpol.value(s): ", (1 - subopt_epsilon) * Vpol.value(s))
        if Vndpol.value(s) < (1 - subopt_epsilon) * Vpol.value(s):
            # print("f")
            return False
    # print("t")
    return True


def ND_greedy_action(mdp: MDP, q: ActionValueFunction, s: State) -> Tuple[Action, float]:
    '''
      Computes the greedy action in the specified state according to the specified action value function.
      The method returns both the action and the value associated with this action in this state.
    '''
    best_action = None
    best_val = None
    for a in mdp.applicable_actions(s):
        val = q.value(s,a)
        if best_val == None or best_val > val:
            best_action = a
            best_val = val
    return best_action, best_val
