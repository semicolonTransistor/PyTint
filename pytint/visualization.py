from pytint.interpreters import Path, FiniteAutomaton
from typing import Dict, List, Iterable, Tuple
from graphviz import Digraph
import random
import string


def render_finite_automaton(automaton: FiniteAutomaton) -> Digraph:
    machine_graph: Digraph = Digraph(engine="dot", format="png")

    edges: Dict[str, Dict[str, List[str]]] = dict()

    # Convert the transition function look up table to symbols on each edge to make drawing easier.
    for start_state in automaton.transitions.keys():
        connections = automaton.transitions[start_state]
        for symbol in connections.keys():
            next_states = connections[symbol]
            if start_state not in edges:  # if there isn't a entry for start node yet
                edges[start_state] = dict()  # initialize entry to empty dict

            if isinstance(next_states, str):
                next_states = [next_states]

            for next_state in next_states:
                if next_state not in edges[start_state]:  # if there isn't an entry for the start/end state combo yet
                    edges[start_state][next_state] = list()  # initialize entry to empty list

                edges[start_state][next_state].append(symbol)  # add the symbol to the appropriate edge.

    # construct the graph

    # add all the nodes
    for state in edges:

        shape = "circle"  # defaults to circle (for non-accepting state)

        if state in automaton.accepting:
            shape = "doublecircle"  # mark accepting states with a double circle

        machine_graph.node(state, shape=shape)  # add the state to graph

    machine_graph.node(".", shape="point")

    for state in edges:
        connections = edges[state]
        for next_state in connections:
            machine_graph.edge(state, next_state, ", ".join(connections[next_state]))

    machine_graph.edge(".", automaton.start)

    return machine_graph


def render_finite_automaton_path(path: Path, automaton: FiniteAutomaton) -> Digraph:

    def _build_path_graph(rest_path: Path, accepting: Iterable[str]) -> Tuple[Digraph, str, bool]:
        sub_graph = Digraph()

        if isinstance(rest_path, str):
            state = rest_path
        else:
            state = rest_path[0]

        shape = "circle"

        if state in accepting:
            shape = "doublecircle"
        mangled_name = ''.join(random.choice(string.ascii_letters) for i in range(10)) + "_" + state

        sub_accepted = False
        if not isinstance(rest_path, str):
            for symbol, sub_path in rest_path[1]:
                sub_sub_graph, node_name, sub_sub_accepted = _build_path_graph(sub_path, accepting)
                sub_accepted = sub_accepted or sub_sub_accepted
                sub_graph.subgraph(sub_sub_graph)
                if sub_sub_accepted:
                    sub_graph.edge(mangled_name, node_name, symbol)
                else:
                    sub_graph.edge(mangled_name, node_name, symbol, color="grey", fontcolor="grey")
        else:
            sub_accepted = state in accepting

        if sub_accepted:
            sub_graph.node(mangled_name, state, shape=shape)
        else:
            sub_graph.node(mangled_name, state, shape=shape, color="grey", fontcolor="grey")

        return sub_graph, mangled_name, sub_accepted

    graph, first_node_name, accepted = _build_path_graph(path, automaton.accepting)
    graph.format = "png"
    graph.node(".", shape="point")
    graph.edge(".", first_node_name)
    return graph
