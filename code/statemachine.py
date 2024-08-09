from dataclasses import dataclass
from typing import Dict, List, Tuple

from MDP import Action, ActionOutcome, MDP, Policy, State

'''
  A State Machine MDP (SMMDP) is an implementation of a state machine 
  where each state is represented by a string 
  and the transitions are enumerated.  
  This is different from, e.g., the DungeonMDP 
  in which a state is an object that is computed on the fly.  
  The benefit of SMMDPs is that they are computed once and for all; 
  the problem with an SMMDP is that they must be computed entirely: 
  if the MDP includes a trillion states, you will never be able to compute it.
'''

class SMState(State):
    def __init__(self, name: str):
        self._name = name

    def __repr__(self) -> str:
        return self._name

    def name(self) -> str: 
        return self._name

class SMAction(Action):
    def __init__(self, name: str):
        self._name = name

    def __repr__(self) -> str:
        return self._name

    def name(self) -> str: 
        return self._name

@dataclass
class SMTransition(): 
    origin: str
    action: str
    prob_distribution: List[Tuple[str, float, float]]

class SMMDP(MDP):
    '''
      An MDP represented as an explicit state machine, 
      i.e., where each state and action is given a name (= string)
      and transitions are defined as a tuples.
    '''
    def __init__(self, 
      transitions: List[SMTransition], 
      initial_state: str):
        self._states: Dict[str, SMState] = {}
        self._actions: Dict[str, SMAction] = {}
        self._transitions: Dict[SMState, Dict[SMAction, List[ActionOutcome]]] = {}

        # Now populate the MDP
        trans: SMTransition = None
        for trans in transitions: 
            origin: SMState = self.get_state(trans.origin)
            action: SMAction = self.get_action(trans.action)
            outcomes = []
            for succname, prob, rew in trans.prob_distribution:
                succ: SMState = self.get_state(succname)
                outcomes.append( ActionOutcome(prob=prob, state=succ, reward=rew) )
            self._transitions[origin][action] = outcomes

        self._initial_state: SMState = self.get_state(initial_state)
    
    def get_state(self, sname: str) -> SMState:
        '''
        Makes sure that the MDP knows about this state
        '''
        if not (sname in self._states):
            s = SMState(sname)
            self._states[sname] = s
            self._transitions[s] = {}
        return self._states[sname]
    
    def get_action(self, aname: str) -> SMAction:
        '''
        Makes sure that the MDP knows about this action
        '''
        if not (aname in self._actions):
            a = SMAction(aname)
            self._actions[aname] = a
        return self._actions[aname]

    def states(self) -> List[State]:
        return [ s for (_,s) in self._states.items() ] # Making a copy to avoid wrong doings

    def actions(self) -> List[Action]:
        return [ a for (_,a) in self._actions.items() ] # Making a copy to avoid wrong doings

    def applicable_actions(self, s: State) -> List[Action]: # Making a copy to avoid wrong doings
        return [ a for (a,_) in self._transitions[s].items()]

    def next_states(self, s: State, a: Action) -> List[ActionOutcome]: # Making a copy to avoid wrong doings
        return self._transitions[s][a].copy()
    
    def initial_state(self) -> State:
        return self._initial_state

    def print(self) -> None:
        print(f'{self.initial_state()}')
        for state in self.states():
            for action in self.applicable_actions(state):
                outcome = self.next_states(state, action)
                print(f'{state} {action} {outcome}')

def read_state_machine(file) -> SMMDP: 
    import re # pip install regex
    exp = re.compile('(\S+)\s+(\S+)\s+(.*)')
    exp2 = re.compile('\(\s*(\S+)\s*,\s*(\S+)\s*,\s*(\S+)\s*\)')
    with open(file,'r') as input:
        initial_state = input.readline().strip()
        transes = []
        for line in input.readlines():
            m = exp.match(line)
            orig = m.group(1)
            action = m.group(2)
            outcome = m.group(3)
            trans = SMTransition(orig, action, exp2.findall(outcome))
            transes.append(trans)
    return SMMDP(transes, initial_state)

def state_machine_from_mdp(mdp: MDP) -> Tuple[SMMDP,Dict[SMState,State],Dict[SMAction,Action]]:
    '''
      Computes an SMMDP that is equivalent to the specified MDP: 
      same number of states, same number of actions, similar transitions, etc.  
      Alongside the SMMDP, the method also returns dictionaries
      that allows one to translate back the states and actions from the SMMDP 
      into the states and actions from the original MDP.
    '''
    state_to_str = {}
    str_to_state = {}
    action_to_str = {}
    str_to_action = {}

    nbstates = [0] # using an array here so that get_state can modify it.
    nbactions = [0]

    transitions = []

    def get_state(state: State) -> str:
        if state in state_to_str:
            return state_to_str[state]
        result = f'state_{nbstates[0]}'
        nbstates[0] += 1
        state_to_str[state] = result
        str_to_state[result] = state
        return result

    def get_action(action: Action) -> str:
        if action in action_to_str:
            return action_to_str[action]
        result = f'act_{nbactions[0]}'
        nbactions[0] += 1
        action_to_str[action] = result
        str_to_action[result] = action
        return result

    str_initial = get_state(mdp.initial_state())
    
    open = set()
    known = set()
    open.add(mdp.initial_state())
    known.add(mdp.initial_state())

    while open:
        state = open.pop()
        str_state = get_state(state)
        for act in mdp.applicable_actions(state):
            str_act = get_action(act)

            # copy the successors in open/known
            for outcome in mdp.next_states(state,act):
                if not outcome.state in known:
                    open.add(outcome.state)
                    known.add(outcome.state)
            
            trans = SMTransition( str_state, str_act,
                [ (get_state(outcome.state),outcome.prob,outcome.reward) 
                  for outcome in mdp.next_states(state,act)]
            )
            transitions.append(trans)

    smmdp = SMMDP(transitions, str_initial)
    return (
        smmdp, 
        { smmdp.get_state(str_state):state for state,str_state in state_to_str.items() },
        { smmdp.get_action(str_act):act for act,str_act in action_to_str.items() }
    )
    
class TranslatedPolicy(Policy):
    '''
      Given two equivalent MDPs m1 and m2, 
      given a dictionary that translates any state from m1 into the equivalent state from m2, 
      and given a dictionary that translates any action from m2 into the equivalent action from m1, 
      given a policy pi for m2, 
      the translated policy is the equivalent of pi for m1.
    '''
    def __init__(self, pol, state_translater, action_translater):
        self.pol_ = pol
        self.state_translater_ = state_translater
        self.action_translater_ = action_translater

    def action(self, state: State) -> Action:
        other_state = self.state_translater_[state]
        other_action = self.pol_.action(other_state)
        act = self.action_translater_[other_action]
        return act


# eof