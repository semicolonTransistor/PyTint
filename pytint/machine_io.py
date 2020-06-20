from pytint.interpreters import FiniteAutomaton
from typing import List, Union, Dict, Iterable
import collections
import yaml


class IncompleteMachine(Exception):
    def __init__(self, missing: str, machine_type: str):
        self.missing = missing
        self.machine_type = machine_type

    def __str__(self):
        return "\"{}\" is required for {} but not provided".format(self.missing, self.machine_type)


class UnsupportedMachine(Exception):
    pass


def load_machine(yaml_input: str, machine_type: str = "", name: str = ""):
    # loads yaml from input
    data = yaml.safe_load(yaml_input)

    # if no type override, attempt to load type from data
    if not machine_type:
        if "type" in data:
            machine_type = str(data["type"]).lower()
        else:
            # can't find machine type
            raise IncompleteMachine("type", "machine")

    if not name and "name" in data:
        name = data["name"]

    if "start" in data:
        start = str(data["start"])
        start
    else:
        raise IncompleteMachine("start", machine_type)

    if machine_type == "dfa" or machine_type == "nfa":
        machine = FiniteAutomaton(name)
        machine.set_start_state(start)
        if "accept-states" in data:
            raw_accepted: Union[any, Iterable[any]] = data["accept-states"]
            if isinstance(raw_accepted, str) or not isinstance(raw_accepted, collections.Iterable):
                raw_accepted = [raw_accepted]
            accepted: List[str] = list(map(lambda x: str(x), raw_accepted))

            for accept_state in accepted:
                machine.add_accepting_state(accept_state)
        else:
            raise IncompleteMachine("accept-states", machine_type)

        if "transitions" in data:
            for transition in data["transitions"]:
                if len(transition) < 3:
                    raise Exception("Transitions are 3-tuples!")

                state: str = str(transition[0])

                raw_symbols: Union[any, Iterable[any]] = str(transition[1])
                if isinstance(raw_symbols, str) or not isinstance(raw_symbols, collections.Iterable):
                    raw_symbols = [raw_symbols]
                symbols: List[str] = list(map(lambda x: str(x), raw_symbols))

                raw_next_states: Union[any, Iterable[any]] = transition[2]
                if isinstance(raw_next_states, str) or not isinstance(raw_next_states, collections.Iterable):
                    raw_next_states = [raw_next_states]
                next_states: List[str] = list(map(lambda x: str(x), raw_next_states))

                for symbol in symbols:
                    if symbol.lower() == "epsilon" or symbol.lower() == "ε":  # process epsilon
                        symbol = "ε"

                    for next_state in next_states:
                        machine.add_transition(state, symbol, next_state)
        else:
            raise IncompleteMachine("transitions", machine_type)

        return machine
    else:
        raise UnsupportedMachine("{} is not a supported machine type!".format(machine_type))


def load_machine_from_file(path: str, machine_type: str = "", name: str = ""):
    with open(path, "r") as f:
        text = f.read()
    return load_machine(text, machine_type, name)
