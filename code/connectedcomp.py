from collections import deque
from typing import Any, List, FrozenSet, Set

import numpy

from MDP import State, MDP


class ConnectedComponent:
    def __init__(self, states: List[State], children: Set[Any]) -> None:
        self.states_ = states
        self.children_ = children

    def states(self) -> List[State]:
        return self.states_

    def children(self) -> List[Any]:
        return self.children_


class CCGraph:
    def __init__(self) -> None:
        self.roots_ = set()  # all connected components can be reached from the roots

    def add_connected_component(self, cc: ConnectedComponent) -> None:
        self.roots_ = self.roots_.difference(cc.children())
        self.roots_.add(cc)

    def roots(self) -> Set[ConnectedComponent]:
        return self.roots_

    def print(self) -> None:
        todo = set()
        node_to_int = {}
        nb_nodes = 0
        for node in self.roots_:
            node_to_int[node] = nb_nodes
            nb_nodes += 1
            todo.add(node)

        while todo:
            node = todo.pop()
            for next in node.children():
                if not next in node_to_int:
                    node_to_int[next] = nb_nodes
                    nb_nodes += 1
                    todo.add(next)
            print(f'{node_to_int[node]} -> {[node_to_int[next] for next in node.children()]}')
            # print(node.states())

    def nb_components(self) -> int:
        open = set()
        closed = set()
        for cc in self.roots():
            open.add(cc)
            closed.add(cc)

        result = 0
        while open:
            cc = open.pop()
            result += 1
            for child in cc.children():
                if child in closed:
                    continue
                open.add(child)
                closed.add(child)

        return result


SCCS = deque()


def compute_connected_components(mdp: MDP) -> CCGraph:
    global SCCS
    result = CCGraph()
    dfn = dict.fromkeys(mdp.states())
    low = dict.fromkeys(mdp.states())
    in_stack = dict.fromkeys(mdp.states())  # 0 -> F; 1 -> T;
    stack = []
    for state in mdp.states():
        # print(dfn[state])
        if dfn[state] is None:
            dfs(mdp, state, dfn, low, stack, in_stack)

    leafBot = ConnectedComponent(SCCS.popleft(), set())
    result.add_connected_component(leafBot)
    while SCCS:
        node = ConnectedComponent(SCCS.popleft(), {leafBot})
        result.add_connected_component(node)
        leafBot = node

    return result


# eof
time = 0


def dfs(mdp: MDP, state, dfn, low, stack, in_stack):
    global time
    global SCCS
    dfn[state] = time
    low[state] = time
    stack.append(state)
    in_stack[state] = 1

    time += 1

    statesCanGo = []
    for action in mdp.applicable_actions(state):
        for outcome in mdp.next_states(state, action):
            s = outcome.state
            statesCanGo.append(s)
    for y in statesCanGo:
        if dfn[y] is None:
            dfs(mdp, y, dfn, low, stack, in_stack)
            low[state] = min(low[state], low[y])
        elif in_stack[y] == 1:
            low[state] = min(low[state], dfn[y])

    if dfn[state] == low[state]:

        pointer = stack[-1]
        SCC = []
        while state.__hash__() != pointer.__hash__():
            s = stack.pop()
            SCC.append(s)
            in_stack[s] = None
            pointer = stack[-1]
        s = stack.pop()
        SCC.append(s)
        in_stack[s] = None
        SCCS.append(SCC)
