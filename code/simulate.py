from typing import Set

from MDP import Action, Policy, State
from dungeon import AdventurerType, DungeonMDP, DungeonState, HireAction, Map, MoveAction, pretty_print_history, probability_of_dying
from dungeon import NoAction

class HandCraftedPolicy(Policy):
    '''
    Defines a policy that works for most dungeon.  
    This policy is not computed by a clever algorithm such a VI, 
    but is based on rules-of-thumbs.

    Essentially, the following rules are used: 
    * If all locations have been visited, do nothing.
    * Otherwise, if your party is not empty, go to the room that looks easiest to reach.
    * Otherwise, find the inn that gets you the best adventurer (regardless of the cost), and go there
    (hire the adventurer if you are already there).
    '''
    def __init__(self, m: Map) -> None:
        self._map = m
        self._computed = {} # a dictionary that records decisions that were already computed.

    def action(self, s: State) -> Action:
        if s in self._computed:
            return self._computed[s]
        result = self.do_compute_action(s)
        self._computed[s] = result
        return result

    def do_compute_action(self, s: State) -> Action:
        dstate: DungeonState = s

        # If all locations have been visited, do nothing
        if dstate.visited_places_ == self.locations():
            return NoAction()

        # If party is not empty, selects the first adventurer, 
        # searches the unvisited room close to a visited room 
        # that it has the max chance of being able to enter (could have proba 0), 
        # and travels towards it.
        if not dstate.party().empty_party():
            atype: AdventurerType = dstate.party().adventurer_types()[0]
            
            best_location = None
            best_proba = -1
            for loc in self.reachable_unvisited_places(dstate):
                if self._map.is_inn(loc) or self._map.is_chest_room(loc):
                    best_location = loc
                    best_proba = 1
                    break # let's stop here!
                # There's a monster in this room
                proba = 1- probability_of_dying(map.room_monster(loc), atype)
                if proba > best_proba:
                    best_location = loc
                    best_proba = proba
                    if best_proba == 1:
                        break

            if best_location == None: # If the map disconnected?
                return NoAction() 

            first_move = self.first_step_towards(dstate.location_, best_location, dstate.visited_places_)
            return MoveAction(first_move, atype)

        # Party is empty.  We now select the pair (adventurer type that can be hired / room to visit) 
        # that maximises the chances of success for the adventurer
        reachables = self.reachable_unvisited_places(dstate)
        availables = self.available_adventurers(dstate)

        best_type = None
        best_inn = None
        best_proba = -1
        for room in reachables:
            if self._map.is_dangerous(room):
                for atype,inn in availables:
                    proba = 1 - probability_of_dying(self._map.room_monster(room), atype)
                    if proba > best_proba:
                        best_type = atype
                        best_inn = inn
                        best_proba = proba

        # we want to go to the best inn!
        # if we are in the inn, we hire the adventurer
        if dstate.location_ == best_inn:
            for price,type in self._map.for_hire(best_inn):
                if type == best_type:
                    return HireAction(best_type, price)

        first_move = self.first_step_towards(dstate.location_, best_inn, dstate.visited_places_)
        return MoveAction(first_move, None)

    def locations(self) -> Set[str]:
        try: 
            self._locations
        except:
            locations = set()
            for loc in self._map.chest_rooms_:
                locations.add(loc)
            for loc in self._map.dangerous_locations_:
                locations.add(loc)
            for loc in self._map.inns_:
                locations.add(loc)
            self._locations = locations
        return self._locations

    def first_step_towards(self, start, end, allowed_location):
        if end in self._map.neighbours(start):
            return end

        # too tired to optimise
        open = []
        distance = {}
        first_move = {}

        # initialise
        for loc in self._map.neighbours(start):
            if not loc in allowed_location:
                continue
            open.append(loc)
            distance[loc] = 1
            first_move[loc] = loc

        while open:
            current_loc = open.pop()
            for nei in self._map.neighbours(current_loc):
                if not nei in allowed_location and nei != end:
                    continue
                new_distance = distance[current_loc] + 1
                if nei in distance and distance[nei] <= new_distance:
                    continue
                open.append(nei)
                distance[nei] = new_distance
                first_move[nei] = first_move[current_loc]
        
        return first_move[end]

    def reachable_unvisited_places(self, dstate: DungeonState):
        result = set()
        for loc in dstate.visited_places_:
            for nei in self._map.neighbours(loc):
                if nei in dstate.visited_places_:
                    continue
                result.add(nei)

        result = list(result) # Want to make sure they are always in the same order
        result.sort()
        return result

    def available_adventurers(self, dstate):
        result = set()
        for loc in dstate.visited_places_:
            if self._map.is_inn(loc):
                for _,atype in self._map.for_hire(loc):
                    result.add((atype,loc))
        result = list(result)
        result.sort()
        return result

if __name__ == '__main__':
    from dungeon import basic_map
    from algos import compute_v_of_policy, simulate

    map = basic_map()
    dg = DungeonMDP(map)
    pol = HandCraftedPolicy(map)

    #h = simulate(mdp=dg, pol=pol, nbsteps=50)
    #pretty_print_history(h)

    #val = compute_v_of_policy(mdp=dg, pol=pol, gamma=.9, stopping_threshold=.01)
    #print(f'Value in initial state: {val.value(dg.initial_state())}')

    pass

# eof