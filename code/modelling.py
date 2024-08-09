from typing import Callable, List
from xmlrpc.client import Boolean
from MDP import Action, ActionOutcome, State, MDP
from dungeon import HireAction, NoAction

EPSILON = 0.001
GAMMA = 0.95


#
# Example: add_cost_to_each_action
#

def add_cost_to_actions(mdp: MDP, action_condition: Callable[[Action], Boolean], c: float) -> MDP:
    class AddCostToEachAction(MDP):
        """
          This implementation of an MDP adds the specified cost to each action
          of the specified MDP that satisfy the specified condition.
          (Adding a cost means reducing the reward.)
        """

        def __init__(self, mdp: MDP, acond, c: float):
            self._mdp = mdp
            self._acond = acond
            self._cost = c

        def states(self) -> List[State]:
            """ Same set of states """
            return self._mdp.states()

        def actions(self) -> List[Action]:
            """ Same set of actions """
            return self._mdp.actions()

        def applicable_actions(self, s: State) -> List[Action]:
            """ Same applicable actions """
            return self._mdp.applicable_actions(s)

        def next_states(self, s: State, a: Action) -> List[ActionOutcome]:
            """
                Modified outcomes.
                Python experts would write this in one line,
                but I choose a method that is easier to parse.
            """
            if not self._acond(a):
                return self._mdp.next_states(s, a)
            old_outcomes = self._mdp.next_states(s, a)
            new_outcomes = []
            for old_outcome in old_outcomes:
                new_outcome = ActionOutcome(old_outcome.prob, old_outcome.state, old_outcome.reward - self._cost)
                new_outcomes.append(new_outcome)
            return new_outcomes

        def initial_state(self) -> State:
            """ Same initial state """
            return self._mdp.initial_state()

    return AddCostToEachAction(mdp, action_condition, c)


def q0_action_condition(act: Action):
    from dungeon import NoAction
    if isinstance(act, NoAction):
        return False
    return True


Q0_answer = 1.8


#
# Question 1
#

def penalise_state_action(mdp: MDP, action_condition: Callable[[Action], Boolean],
                          state_condition: Callable[[State], Boolean], cost: float):
    """
    Returns an MDP that adds the specified cost
    to actions that satisfy the specified condition
    when they are performed in states that satisfy the specified condition.
    """
    class AddSpecifiedCostToSpecifiedAction(MDP):
        def __init__(self, mdp: MDP, acond, scond, c: float):
            self._mdp = mdp
            self._acond = acond
            self._scond = scond
            self._cost = c

        def states(self) -> List[State]:
            """ Same set of states """
            return self._mdp.states()

        def actions(self) -> List[Action]:
            """ Same set of actions """
            return self._mdp.actions()

        def applicable_actions(self, s: State) -> List[Action]:
            """ Same applicable actions """
            return self._mdp.applicable_actions(s)

        def next_states(self, s: State, a: Action) -> List[ActionOutcome]:
            if self._scond(s):
                if self._acond(a):
                    old_outcomes = self._mdp.next_states(s, a)
                    new_outcomes = []
                    for old_outcome in old_outcomes:
                        new_outcome = ActionOutcome(old_outcome.prob, old_outcome.state, old_outcome.reward - self._cost)
                        new_outcomes.append(new_outcome)
                    return new_outcomes
                else:
                    return self._mdp.next_states(s, a)
            else:
                return self._mdp.next_states(s, a)


        def initial_state(self) -> State:
            """ Same initial state """
            return self._mdp.initial_state()

    return AddSpecifiedCostToSpecifiedAction(mdp, action_condition, state_condition, cost)


def q1_action_condition(act: Action):
    from dungeon import MoveAction
    if not isinstance(act, MoveAction):
        return False
    if act.locname_.startswith('inn_'):
        return True
    return False


def q1_state_condition(st: State):
    return not st.party_.empty_party()


Q1_answer = 45
''' TODO:
 Use the result of penalise_state_action
 with the parameters q1_action_condition and q1_state_condition.
 Use VI (or any other algorithm) to determine which value to give to cost 
 so that the expected return in the initial state ranges from 30 and 40.
'''


#
# Question 2
#

def forbid_actions_in_states(mdp: MDP, action_condition: Callable[[Action], Boolean],
                             state_condition: Callable[[State], Boolean]):
    """
      Forbids all actions that satisfy the action_condition
      in states that satisfy the state_condition,
      *except* if no action is applicable in the state.
    """
    class ForbidSpecifiedAction(MDP):
        def __init__(self, mdp: MDP, acond, scond):
            self._mdp = mdp
            self._acond = acond
            self._scond = scond

        def states(self) -> List[State]:
            """ Same set of states """
            return self._mdp.states()

        def actions(self) -> List[Action]:
            """ Same set of actions """
            return self._mdp.actions()

        def applicable_actions(self, s: State) -> List[Action]:
            """ Same applicable actions """
            if self._scond(s):
                if self._mdp.applicable_actions(s):
                    new_actions = []
                    old_acitons = self._mdp.applicable_actions(s)
                    for action in old_acitons:
                        if not self._acond(action):
                            new_actions.append(action)
                    if new_actions:
                        return new_actions
                    else:
                        return self._mdp.applicable_actions(s)
                else:
                    return self._mdp.applicable_actions(s)
            else:
                return self._mdp.applicable_actions(s)



        def next_states(self, s: State, a: Action) -> List[ActionOutcome]:
            return self._mdp.next_states(s, a)

        def initial_state(self) -> State:
            """ Same initial state """
            return self._mdp.initial_state()

    return ForbidSpecifiedAction(mdp, action_condition, state_condition)


def q2_action_condition1(act: Action):
    from dungeon import HireAction
    if not isinstance(act, HireAction):
        return False
    if act.adventurer_type_._name == 'wizard':
        return True
    return False


def q2_state_condition1(st: State):
    content_of_party = st.party_.adventurer_types()
    for type in content_of_party:
        if type._name == 'soldier':
            return False
    return True


Q2_answer1 = 51.597
''' TODO
 Compute the value of the initial state 
 when using forbid_actions_in_states with parameters q2_action_condition1 and q2_state_condition1.
'''


def q2_action_condition2(act: Action):
    if isinstance(act, HireAction):
        return False
    return True


def q2_state_condition2(st: State):
    return True


Q2_answer2 = 50.808
''' TODO
 Compute the value of the initial state 
 when using forbid_actions_in_states with parameters q2_action_condition2 and q2_state_condition2.
'''


#
# Question 3
#

def limit_action_number(mdp: MDP, action_condition: Callable[[Action], Boolean], limit: int):
    """
     Limits the number of times that an action satisfying the specified condition can be performed.
    """
    class LimitActionNumber(MDP):
        def __init__(self, mdp: MDP, acond, limit):
            self._mdp = mdp
            self._acond = acond
            self._limit = limit
            self._actionsWithLimits = dict()
            for s in self._mdp.states():
                for a in self._mdp.applicable_actions(s):
                    if self._acond(a):
                        self._actionsWithLimits[a] = limit

        def states(self) -> List[State]:
            """ Same set of states """
            return self._mdp.states()

        def actions(self) -> List[Action]:
            """ Same set of actions """
            return self._mdp.actions()

        def applicable_actions(self, s: State) -> List[Action]:
            """ Same applicable actions """
            # return self._mdp.applicable_actions(s)
            outActions = []
            actions = self._mdp.applicable_actions(s)
            # print("actions: ", actions)
            if len(actions) > 1:
                for a in actions:
                    # if a not in self._actionsWithLimits.keys():
                    #     self._actionsWithLimits[a] = limit
                    if a in self._actionsWithLimits.keys():
                        # print(a)
                        # # print(a in mdp.actions())
                        # print(self._actionsWithLimits[a])

                        if self._actionsWithLimits[a] > 0:
                            outActions.append(a)
                        # self._actionsWithLimits[a] = self._actionsWithLimits[a] - 1
                        # if self._actionsWithLimits[a] <= 0:
                        #     self._actionsWithLimits[a] = 0
                    else:
                        outActions.append(a)
                # print("returnLong: ", outActions)
                # print("--------")
                return outActions
            else:
                # print("returnShort: ", actions)
                # print("--------")

                return actions

        def next_states(self, s: State, a: Action) -> List[ActionOutcome]:
            if a in self._actionsWithLimits.keys():
                self._actionsWithLimits[a] = self._actionsWithLimits[a] - 1
                if self._actionsWithLimits[a] <= 0:
                    self._actionsWithLimits[a] = 0

            return self._mdp.next_states(s, a)

        def initial_state(self) -> State:
            """ Same initial state """
            return self._mdp.initial_state()

    return LimitActionNumber(mdp, action_condition, limit)


def q3_action_condition(act: Action):
    if isinstance(act, HireAction):
        return True
    return False


Q3_answer = ''' TODO
 Use the result of limit_action_number
 with the parameter q3_action_condition.
 Use VI (or any other algorithm) to determine which value to give to limit
 so that the expected return in the initial state ranges from 30 to 40.
'''

# eof
