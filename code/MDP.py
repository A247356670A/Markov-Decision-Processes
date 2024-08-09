# MDP.py
# Contains classes and methods to represent and manipulate MDPs, policies, and values.

from __future__ import annotations  # necessary for typing hint references to class not completely defined yet
# __future__ does not work with Python3.7<
from typing import List, Tuple, Optional
from dataclasses import dataclass


class State:
    pass


class Action:
    pass


@dataclass
class ActionOutcome():
    '''
      Represents an outcome of executing an action in a state.  
      The outcome has a probability, it leads to a state, and it returns a reward.
    '''
    prob: float
    state: State
    reward: float


class MDP:
    '''
      This class is the basic interface for an MDP.
      Implementations of MDPs include SMMDP in file statemachine.py
    '''

    def states(self) -> List[State]:
        pass

    def actions(self) -> List[Action]:
        pass

    def applicable_actions(self, s: State) -> List[Action]:
        pass

    def next_states(self, s: State, a: Action) -> List[ActionOutcome]:
        '''
          Returns the possible outcomes of performing action a in state s.  
          Each outcome is a tuple (prob,state,reward) where
          * prob is the probability that executing the action yields this outcome;
          * state is the state that the MDP ends up in;
          * reward is the reward associated with this action.
        '''
        pass

    def initial_state(self) -> State:
        pass


class Policy:
    '''
        The interface for a deterministic Markov Policy
    '''

    def action(self, s: State) -> Action:
        print(f'{type(self).__name__} action function not implemented')


class ExplicitPolicy(Policy):
    '''
      A deterministic Markovian Policy 
      explicitly represented as a dictionary 
      where the default action is the *first* applicable action 
      as returned by the MDP.
    '''

    def __init__(self, mdp: MDP):
        self._mdp = mdp
        self._explicit_decision = {}

    def set_action(self, s: State, a: Action):
        self._explicit_decision[s] = a

    def action(self, s: State):
        if not s in self._explicit_decision:
            self.set_action(s, next(
                iter(self._mdp.applicable_actions(s))))  # takes the first action from the set of applicable actions
        return self._explicit_decision[s]


class History:
    def __init__(
            self,
            mdp: Optional[MDP] = None,
            init_state: Optional[State] = None,
            h: Optional[History] = None
    ):
        '''
          Implementation notes: self._seq contains a sequence 
          (state0, action1, reward1, state1, ..., actionk, rewardk, statek)
        '''
        if not h is None:
            self._mdp = h._mdp
            self._seq = h._seq.copy()
            return
        self._mdp = mdp
        self._seq = [init_state] if not init_state is None else [mdp.initial_state()]

    def __repr__(self):
        strings = []
        for o in self._seq:
            strings.append(str(o))
        return ' '.join(strings)

    def pretty_repr(self) -> List[str]:
        strings = []
        for i in range(self.length()):
            strings.append(str(self.state(i)) + '\taction: ' + str(self.action(i)) + '\treward: ' + str(self.reward(i)))
        strings.append(str(self.state(self.length())))
        return strings

    def add(self, act: Action, state: State, rew: float) -> None:
        self._seq.append(act)
        self._seq.append(rew)
        self._seq.append(state)

    def state(self, i) -> State:
        '''
          From 0 to length() inclusive
        '''
        return self._seq[i * 3]

    def action(self, i) -> Action:
        '''
          From 0 to length()-1 inclusive
        '''
        return self._seq[1 + (i * 3)]

    def reward(self, i) -> float:
        '''
          From 0 to length()-1 inclusive
        '''
        return self._seq[2 + (i * 3)]

    def length(self) -> int:
        return len(self._seq) // 3

    def last_state(self) -> State:
        return self.state(self.length())

# eof
