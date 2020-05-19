from pytint.interpreters import DeterministicFiniteAutomaton, NonDeterministicFiniteAutomaton
from pytint.interpreters import DeterministicTransitions, NonDeterministicTransitions
from typing import List, Union, Dict, Iterable
import collections
import yaml


def load_dfa(ymal_input):
    if isinstance(ymal_input, str):
        ymal_input = open(ymal_input, "r")

    data = yaml.safe_load(ymal_input)
    start: str = str(data["start"])
    raw_accepted: Union[any, Iterable[any]] = data["accept-states"]
    if isinstance(raw_accepted, str) or not isinstance(raw_accepted, collections.Iterable):
        raw_accepted = [raw_accepted]
    accepted: List[str] = list(map(lambda x: str(x), raw_accepted))

    if "name" in data:
        name = data["name"]
    else:
        name = "Deterministic Finite Automaton"

    transitions: DeterministicTransitions = dict()

    for transition in data["transitions"]:
        if len(transition) < 3:
            raise Exception("Syntax Error in Ymal")

        state: str = str(transition[0])
        symbol: str = str(transition[1])
        next_state: str = str(transition[2])

        if state not in transitions:
            transitions[state] = dict()

        transitions[state][symbol] = next_state
    print(transitions)
    print(accepted)
    return DeterministicFiniteAutomaton(transitions, start, accepted, name)


def load_nfa(yaml_input):
    if isinstance(yaml_input, str):
        yaml_input = open(yaml_input, "r")

    data = yaml.safe_load(yaml_input)
    start: str = str(data["start"])
    raw_accepted: Union[any, Iterable[any]] = data["accept-states"]
    if isinstance(raw_accepted, str) or not isinstance(raw_accepted, collections.Iterable):
        raw_accepted = [raw_accepted]
    accepted: List[str] = list(map(lambda x: str(x), raw_accepted))

    if "name" in data:
        name = data["name"]
    else:
        name = "Deterministic Finite Automaton"

    transitions: NonDeterministicTransitions = dict()

    for transition in data["transitions"]:
        if len(transition) < 3:
            raise Exception("Syntax Error in Ymal")

        state: str = str(transition[0])

        symbol: str = str(transition[1])
        if symbol.lower() == "epsilon" or symbol.lower() == "ε":  # process epsilon
            symbol = "ε"

        raw_next_states: Union[any, Iterable[any]] = transition[2]
        if isinstance(raw_next_states, str) or not isinstance(raw_next_states, collections.Iterable):
            raw_next_states = [raw_next_states]
        next_states: List[str] = list(map(lambda x: str(x), raw_next_states))

        if state not in transitions:
            transitions[state] = dict()

        transitions[state][symbol] = next_states
    print(transitions)
    print(accepted)
    return NonDeterministicFiniteAutomaton(transitions, start, accepted, name)
