from __future__ import annotations # necessary for typing hint references to class not completely defined yet
# __future__ does not work with Python3.7<
from typing import Dict, FrozenSet, List, Optional, Set, Tuple
from MDP import Action, ActionOutcome, History, MDP, State

class MonsterType:
    def __init__(self, name: str, st: float, ma: float):
        '''
        A monster type is represented by its name, its physical strength, and its magic power.
        '''
        self._name = name
        self._st = st
        self._ma = ma

    def __repr__(self) -> str:
        return self._name

    def strength(self) -> float: 
        return self._st

    def magic(self) -> float:
        return self._ma

class AdventurerType:
    def __init__(self, name: str, st: float, ma: float):
        '''
        An adventurer type is represented by its name, its physical strength, and its magic power.
        '''
        self._name = name
        self._st = st
        self._ma = ma

    def __repr__(self) -> str:
        return self._name

    def __hash__(self) -> int:
        return self._name.__hash__() # Assumes that there cannot be two different types with the same name

    ''' The following methods are used to order different instances.  '''
    def __eq__(self, other) -> bool:
        if not type(self) == type(other):
            return False
        return self._name == other._name

    def __le__(self, other) -> bool:
        return self._name.__le__(other._name)

    def __lt__(self, other) -> bool:
        return self._name.__lt__(other._name)

    def strength(self) -> float: 
        return self._st

    def magic(self) -> float:
        return self._ma

def probability_of_dying(m: MonsterType, a: AdventurerType) -> float:
    '''
      Indicates the probability (between 0 and 1) that an adventurer of specified type
      will die while fighting a monster of specified type.  
      The way this is computed is not particularly important.  
    '''
    return min(1, max(0, m.strength() - a.strength()) + max(0, m.magic() - a.magic()))

class Map:
    '''
      This class represents a map of the dungeon that the adventurers will travel on.  
      The map is comprised of rooms (represented by a string, e.g., 'Room X').  
      Some rooms are dangerous (contain monsters), 
      some are inns (where adventurers can be hired), 
      some contain chests.  
      You don't need to understand how this class works.
    '''
    def __init__(self):
        '''
          Creates an empty map.
        '''
        # Locations are represented by strings
        self.starting_location_: str = None
        # three types of location
        self.dangerous_locations_: Dict[str,MonsterType] = {} # What type of monster in this location
        self.inns_: Dict[str,Tuple[int,AdventurerType]] = {} # What adventurer, and at what cost in this location
        self.chest_rooms_: Dict[str,int] = {} # How much money in this location
        # neighbours
        self.neighbours_: Dict[str,Set[str]] = {} # Set of locations next to this location

    ''' The following methods modify the map.  '''
    def create_dangerous_location(self, name: str, monster: MonsterType):
        self.dangerous_locations_[name] = monster
        self.neighbours_[name] = set()

    def create_inn(self, name: str, for_hire: List[Tuple[int,AdventurerType]]):
        ''' 
        for_hire is a list of cost per adventurer type.  
        For instance, a warrior costs 10, a magician costs 15, etc.
        '''
        self.inns_[name] = for_hire
        self.neighbours_[name] = set()

    def create_chest_room(self, name: str, reward: int):
        self.chest_rooms_[name] = reward
        self.neighbours_[name] = set()

    def set_initial_location(self, locname: str) -> None:
        self.starting_location_ = locname

    def add_path(self, locname1: str, locname2: str):
        '''
          Adds a path between the two specified locations.
        '''
        self.neighbours_[locname1].add(locname2)
        self.neighbours_[locname2].add(locname1)

    ''' Access methods. '''

    def is_inn(self, locname: str) -> bool:
        return locname in self.inns_

    def is_dangerous(self, locname: str) -> bool:
        return locname in self.dangerous_locations_

    def is_chest_room(self, locname: str) -> bool:
        return locname in self.chest_rooms_

    def room_reward(self, locname: str) -> int:
        ''' The reward for stepping into the room (default is 0) '''
        if locname in self.chest_rooms_:
            return self.chest_rooms_[locname]
        return 0

    def for_hire(self, locname: str) -> List[Tuple[int,AdventurerType]]:
        '''
        Assuming the specified location is an inn,  
        returns a list of cost per adventurer type.  
        For instance, a warrior costs 10, a magician costs 15, etc.
        An inn is assumed to have an infinite supply of adventurers.
        '''
        return self.inns_[locname]

    def room_monster(self, locname: str) -> MonsterType:
        return self.dangerous_locations_[locname]

    def get_initial_location(self) -> str:
        return self.starting_location_

    def locations(self) -> Set[str]:
        return self.neighbours_.keys()

    def neighbours(self, locname: set) -> Set[str]:
        '''
        Indicates the locations that can be reached from the specified location.
        '''
        return self.neighbours_[locname]

def collect_adventurer_types(map: Map) -> Set[Tuple[int,AdventurerType]]:
    '''
    Collects the types of all adventurers that can be hired in this map.
    '''
    result = set()
    for _, offer in map.inns_.items():
        for cost,type in offer:
            result.add((cost,type))
    return result

PARTY_MAX_SIZE = 2
class Party:
    '''
    This class represents a party of hero.  A party is essentially a set of adventurers.
    '''
    def __init__(self, party: Optional[Party] = None, add: Optional[AdventurerType] = None, rem: Optional[AdventurerType] = None):
        '''
        Creates a party that contains the specified party + add - rem
        '''
        # We store the number of adventurers of each type in a dictionary
        advs: Dict[AdventurerType,int] = {}
        if not party is None:
            for (ad,i) in party.adventurers_:
                advs[ad] = i
        if not add is None:
            if not add in advs:
                advs[add] = 0
            advs[add] += 1
        if not rem is None:
            # We assume rem is in advs
            advs[rem] -= 1
            if advs[rem] == 0:
                del advs[rem]

        # We now need to make an hashable version of the dictionary.
        # Dictionaries and lists are not hashable in python.
        # There is no frozendict in python (actually, seems there is in Python 3.10), 
        # so we create a tuple of pairs and sort them
        self.adventurers_: Tuple[Tuple[AdventurerType,int]] = tuple([ 
            (t,advs[t]) for t in sorted(advs.keys())
        ])

    def __eq__(self, party) -> bool:
        return self.adventurers_ == party.adventurers_

    def __repr__(self) -> str:
        return ','.join([f'{adtype}->{nb}' for (adtype,nb) in self.adventurers_])

    def __hash__(self) -> int:
        return self.adventurers_.__hash__()

    def empty_party(self) -> bool: 
        '''
        Indicates if the party is empty
        '''
        return len(self.adventurers_) == 0

    def full(self) -> bool:
        '''
        Indicates if the party is full (cannot accept more adventurers)
        '''
        return self.size() == PARTY_MAX_SIZE

    def size(self) -> int:
        ''''
        Number of adventurers in the party
        '''
        return sum( [i for (_,i) in self.adventurers_] )

    def adventurer_types(self) -> List[AdventurerType]:
        '''
        Indicates the types of adventurers in the party
        '''
        return [ t for (t,_) in self.adventurers_ ]

    def nb_adventurers_of_type(self, adtype: AdventurerType) -> int: # assumes != 0
        return self.adventurers_[adtype]

class DungeonState(State):
    '''
    A dungeon state is defined by the current location, 
    the list of locations that have already been visited, 
    and the current party.
    '''
    def __init__(self, state: Optional[DungeonState] = None, 
          location: Optional[str] = None, 
          add: Optional[AdventurerType] = None, 
          rem: Optional[AdventurerType] = None
          ):
        '''
        Creates a new dungeon state from the specified state 
        where the party is now in the specified location, 
        the first specified adventurer (add) is added to the party, 
        and the second specified adventurer (rem) is removed from the party.
        '''
        self.party_: Party = Party() if state is None else Party(state.party_, add=add, rem=rem)
        self.location_: str = location if location is not None else (state.location_ if state is not None else None)
        visited = set() if state is None else set(state.visited_places_)
        if not location is None:
            visited.add(location)
        self.visited_places_: FrozenSet[str] = frozenset(visited)

    def __eq__(self, state) -> bool:
        if not self.party_ == state.party_:
            return False
        if not self.location_ == state.location_:
            return False
        if not self.visited_places_ == state.visited_places_:
            return False
        return True

    def __repr__(self) -> str:
        from colorama import Fore
        party_string = Fore.RED + f'Party: {self.party_}' + Fore.RESET
        location_string = Fore.BLUE + f'Loc: {self.location_}' + Fore.RESET
        visited_string = Fore.GREEN + f'Visited: {",".join(self.visited_places_)}' + Fore.RESET

        return f'{party_string} -- {location_string} -- {visited_string}'

    def __hash__(self) -> int:
        v1 = self.party_.__hash__()
        v2 = self.location_.__hash__()
        v3 = self.visited_places_.__hash__()
        return v1 + v2 + v3 # it's a good hashing function assuming all other hashing functions are good

    def has_visited(self, locname: str) -> bool:
        '''
        Has the party already visited the specified location?
        '''
        return locname in self.visited_places_

    def party(self) -> Party:
        return self.party_

class DungeonAction(Action):
    '''
    Generic class for actions in the dungeon MDP. 
    The classes are actually implemented below.
    '''
    def next_states(self, state: DungeonState, map: Map) -> List[ActionOutcome]:
        '''
          Indicates the possible outcomes when this action is applied in the specified state. 
          ActionOutcome is described in MDP.py
        '''
        pass

class HireAction(DungeonAction):
    '''
    The action of hiring the specified adventurer at the specified price.  
    This action has only one outcome.
    '''
    def __init__(self, adventurer_type, price):
        self.adventurer_type_ = adventurer_type
        self.price_ = price

    def __repr__(self) -> str:
        return f'Hire {self.adventurer_type_._name} for {self.price_}'

    def __hash__(self) -> int:
        return self.adventurer_type_.__hash__() + self.price_

    def __eq__(self, act) -> bool: 
        if not type(self) == type(act):
            return False
        return (self.adventurer_type_ == act.adventurer_type_) and (self.price_ == act.price_)

    def next_states(self, state: DungeonState, map: Map) -> List[ActionOutcome]:
        new_state = DungeonState(state=state,add=self.adventurer_type_)
        return [ ActionOutcome(prob=1.0, state=new_state, reward=-self.price_) ]

class MoveAction(DungeonAction):
    '''
    The action of moving in the dungeon.  
    This action indicates: 
    * where the party is moving to;
    * what type of adventurer is going first.  
    If the party moves into a new room with a monster, 
    the first adventurer must fight the monster.  
    If the adventurer dies, the party stays in their current location 
    (and the first adventurer is dead).  
    Otherwise, the party moves in.
    '''
    def __init__(self, locname: str, adv: AdventurerType):
        self.locname_: str = locname
        self.adv_: AdventurerType = adv

    def __repr__(self) -> str:
        return f'Move {self.locname_} {self.adv_}'

    def __hash__(self) -> int:
        return self.locname_.__hash__() + self.adv_.__hash__()

    def __eq__(self, act) -> bool:
        if not type(self) == type(act):
            return False
        return self.locname_ == act.locname_ and self.adv_ == act.adv_

    def next_states(self, state: DungeonState, map: Map) -> List[ActionOutcome]:
        # if the new place is already visited, just move in
        if state.has_visited(self.locname_):
            new_state = DungeonState(state=state, location=self.locname_)
            return [ ActionOutcome(prob=1.0,state=new_state,reward=0)]

        # if the new place is not dangerous, just move and collect the reward if any
        if not map.is_dangerous(self.locname_):
            new_state = DungeonState(state=state, location=self.locname_)
            reward = map.room_reward(self.locname_)
            return [ ActionOutcome(prob=1.0,state=new_state,reward=reward)]

        # visiting a dangerous location
        dying_prob = probability_of_dying(map.room_monster(self.locname_), 
            self.adv_)
        success_state = DungeonState(state=state, location=self.locname_)
        fail_state = DungeonState(state=state, rem=self.adv_)

        result = []
        if dying_prob > 0:
            result.append( ActionOutcome(prob=dying_prob, state=fail_state, reward=0) )
        if dying_prob < 1:
            result.append( ActionOutcome(prob=1-dying_prob, state=success_state, reward=0) )
        return result

class NoAction(DungeonAction):
    def __eq__(self, act) -> bool:
        if not type(self) == type(act):
            return False
        return True

    def __repr__(self) -> str:
        return 'No Action'

    def __hash__(self) -> int:
        return self.__repr__().__hash__()

    def next_states(self, state: DungeonState, map: Map) -> List[ActionOutcome]:
        return [ ActionOutcome(prob=1.0,state=state,reward=0) ]

def reachable_states(mdp: MDP, start: Optional[State] = None) -> List[State]:
    '''
    Computes the list of states that are reachable in the specified mdp.
    '''
    result = set()
    open = set() # we need to check the successors of these states.

    if start is None:
        start = mdp.initial_state()
    result.add(start)
    open.add(start)

    while open:
        state = open.pop()
        for act in mdp.applicable_actions(state):
            for outcome in mdp.next_states(state, act):
                next_state = outcome.state
                if next_state in result:
                    continue
                result.add(next_state)
                open.add(next_state)
    
    return list(result)

class DungeonMDP(MDP):
    '''
      The MDP that represents the travelling into the dungeon.
    '''
    def __init__(self, map: Map):
        self.map_ = map
        self.reachable_states_ = None # lazy computation
        self.actions_ = None

    def states(self) -> List[State]:
        if self.reachable_states_ == None:
            self.reachable_states_ = reachable_states(self)
        return self.reachable_states_

    def actions(self) -> List[Action]:
        if self.actions_ == None:
            result = { NoAction() }
            types = set()
            for cost,type in collect_adventurer_types(self.map_):
                act = HireAction(type, cost)
                result.add(act)
                types.add(type)
            for type in types:
                for loc in self.map_.locations():
                    act = MoveAction(loc,type)
                    result.add(act)
            self.actions_ = list(result)
            
        return self.actions_

    def applicable_actions(self, s: State) -> List[Action]:
        result = [ NoAction() ]
        map = self.map_
        locname = s.location_
        party = s.party_

        # hire an adventurer
        if map.is_inn(locname) and not party.full():
            for price,adtype in map.for_hire(locname):
                act = HireAction(adtype, price)
                result.append(act)

        # move to a new location
        for type in party.adventurer_types():
            for loc in map.neighbours(locname):
                act = MoveAction(loc,type)
                result.append(act)

        # can also move to visited room if there is noone in the party
        if party.empty_party():
            for loc in map.neighbours(locname):
                if s.has_visited(loc):
                    act = MoveAction(loc,None)
                    result.append(act)
            
        return result

    def next_states(self, s: State, a: Action) -> List[ActionOutcome]:
        # a should be a DungeonAction, in which case we can call the following method:
        return a.next_states(s, self.map_)
    
    def initial_state(self) -> DungeonState:
        return DungeonState(location=self.map_.get_initial_location())

# end of class

def basic_map() -> Map:
    # adventurers
    peon = AdventurerType('peon', st=0, ma=0)
    wizard = AdventurerType('wizard', st=.1, ma=1.0)
    soldier = AdventurerType('soldier', st=.5, ma=.0)
    # monsters
    goblin = MonsterType('goblin', st=.3, ma=.0)
    fimir = MonsterType('fimir', st=.7, ma=.1)
    sorcerer = MonsterType('sorcerer', st=.2, ma=1.4)
    # map
    map = Map()
    map.create_inn('inn_start', for_hire=[(10,peon),(100,soldier)])
    map.set_initial_location('inn_start')
    map.create_inn('inn_market', for_hire=[(8,peon),(50,soldier),(100,wizard)])
    map.create_dangerous_location('room1', fimir)
    map.create_dangerous_location('room2', goblin)
    map.create_dangerous_location('room3', sorcerer)
    map.create_dangerous_location('room4', goblin)
    map.create_chest_room('smallchest', 30)
    map.create_chest_room('largechest', 500)
    map.add_path('inn_start','room1')
    map.add_path('inn_start','room2')
    map.add_path('inn_start','room4')
    map.add_path('inn_market','room2')
    map.add_path('room1','room2')
    map.add_path('room1','room3')
    map.add_path('room1','room4')
    map.add_path('room3','largechest')
    map.add_path('room4','smallchest')

    return map

def pretty_print_history(h: History):
    for i in range(h.length()+1):
        print(h.state(i))
        if i != h.length():
            print(f'\u2193 {h.action(i)} -- Reward = {h.reward(i)}')
    pass

if __name__ == "__main__":

    map = basic_map()
    mdp = DungeonMDP(map)

    import statemachine

    smmdp, statedict, actiondict = statemachine.state_machine_from_mdp(mdp)
    reverse_statedict = {}
    for smstate, state in statedict.items():
        reverse_statedict[state] = smstate

    from algos import value_iteration
    smpol, svalue = value_iteration(smmdp, .99, .01)

    print('--')

    from algos import simulate
    pol = statemachine.TranslatedPolicy(smpol, reverse_statedict, actiondict)
    h = simulate(mdp, pol, 20)
    pretty_print_history(h)

# eof