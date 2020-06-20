from pytint.interpreters import FiniteAutomaton, FAComputationHistory
from typing import Dict, List, Iterable, Tuple
from graphviz import Digraph
import random
import string


def render_finite_automaton(automaton: FiniteAutomaton) -> Digraph:
    machine_graph: Digraph = Digraph(engine="dot", format="png")

    edges: Dict[str, Dict[str, List[str]]] = dict()

    # Convert the transition function look up table to symbols on each edge to make drawing easier.
    for start_state in automaton.transitions:
        connections = automaton.transitions[start_state]
        for symbol in connections.keys():
            next_states = connections[symbol]
            if start_state not in edges:  # if there isn't a entry for start node yet
                edges[start_state] = dict()  # initialize entry to empty dict

            for next_state in next_states:
                # add an entry for the next_state if there isn't one already. Assuring all reachable states have
                # an entry.
                if next_state not in edges:
                    edges[next_state] = dict()

                if next_state not in edges[start_state]:  # if there isn't an entry for the start/end state combo yet
                    edges[start_state][next_state] = list()  # initialize entry to empty list

                edges[start_state][next_state].append(symbol)  # add the symbol to the appropriate edge.

    # construct the graph

    # add all the nodes
    for state in edges:

        shape = "circle"  # defaults to circle (for non-accepting state)

        if state in automaton.accept_states:
            shape = "doublecircle"  # mark accepting states with a double circle

        machine_graph.node(state, shape=shape)  # add the state to graph

    machine_graph.node(".", shape="point")

    for state in edges:
        connections = edges[state]
        for next_state in connections:
            machine_graph.edge(state, next_state, ", ".join(connections[next_state]))

    machine_graph.edge(".", automaton.start_state)

    return machine_graph


def render_finite_automaton_history(automaton: FiniteAutomaton, history: FAComputationHistory = None) -> Digraph:
    # use the history of the automaton by default
    if history is None:
        history = automaton.computation_history

    graph = Digraph()

    # return empty graph if
    if not history or not history[0]:
        return graph

    # set up initial state
    graph.node("start", shape="point")

    # mark as accepting if the state is in accepting states and the tape is empty
    if history[0][0].state in automaton.accept_states and not history[0][0].tape:
        graph.node("0-0", shape="doublecircle", label=history[0][0].state, rank="0")
    else:
        graph.node("0-0", shape="circle", label=history[0][0].state, rank="0")

    graph.edge("start", "0-0")

    for i in range(1, len(history)):
        with graph.subgraph() as s:
            for j in range(len(history[i])):
                configuration = history[i][j]

                # mark as accepting if the state is in accepting states and the tape is empty
                if configuration.state in automaton.accept_states and not configuration.tape:
                    shape = "doublecircle"
                else:
                    shape = "circle"

                s.node("{row}-{col}".format(row=i, col=j), shape=shape, label=configuration.state, rank=str(i))
                s.edge("{row}-{col}".format(row=i-1, col=configuration.prev_index),
                       "{row}-{col}".format(row=i, col=j),
                       label=configuration.symbol_read)
    return graph

