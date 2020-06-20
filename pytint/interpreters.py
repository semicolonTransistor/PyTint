from typing import List, Deque, Dict, Set, Iterable
Symbol = str
State = str


class FAConfiguration:
    def __init__(self, tape: List[Symbol], state: State, symbol_read: Symbol, prev_index: int, epsilon_set=None):

        if epsilon_set is None:
            epsilon_set = set()

        self.tape = tape
        self.state = state
        self.prev_index = prev_index
        self.epsilon_set = epsilon_set
        self.symbol_read = symbol_read


FAConfigurations = List[FAConfiguration]
FAComputationHistory = List[FAConfigurations]

FATransitions = Dict[State, Dict[Symbol, Set[State]]]


class FiniteAutomaton:
    def __init__(self, name="FA"):
        self.transitions: FATransitions = dict()
        self.start_state: State = ""
        self.accept_states: Set[State] = set()
        self.current_configurations: FAConfigurations = list()
        self.computation_history: FAComputationHistory = list()
        self.complete: bool = False
        self.accepted: bool = False
        self.name: str = name

    def add_transition(self, state: State, symbol: Symbol, next_state: State):
        if state not in self.transitions:
            self.transitions[state] = dict()

        if symbol not in self.transitions[state]:
            self.transitions[state][symbol] = set()

        self.transitions[state][symbol].add(next_state)

    def set_start_state(self, state: State):
        self.start_state = state

    def add_accepting_state(self, state: State):
        self.accept_states.add(state)

    def start_new_computation(self, tape: Iterable[Symbol]):
        # reset internal states and prepare for new computation
        self.current_configurations = list()
        self.complete = False
        self.accepted = False
        self.computation_history = list()

        # set up the starting state
        self.current_configurations.append(FAConfiguration(list(tape), self.start_state, "", -1))
        self.computation_history.append(self.current_configurations)

    def simulate_one_step(self) -> bool:
        # do not execute if computation is already completed
        if self.complete:
            return True

        new_configurations: FAConfigurations = list()
        for index in range(len(self.current_configurations)):
            this_config = self.current_configurations[index]

            # terminate computation if an accepting state has been reached with an empty tape
            if this_config.state in self.accept_states and not this_config.tape:
                self.complete = True
                self.accepted = True
                return True

            # check if there is a entry for the state in the transition function
            if this_config.state not in self.transitions:
                # skip this config since there is no transition function out of this state.
                continue

            # check for epsilon transitions
            # marked with lower case epsilon(unicode code point 03F5)
            if "ϵ" in self.transitions[this_config.state]:
                for next_state in self.transitions[this_config.state]["ϵ"]:
                    if next_state not in this_config.epsilon_set:
                        epsilon_set = this_config.epsilon_set.copy()
                        epsilon_set.add(next_state)
                        new_configurations.append(FAConfiguration(this_config.tape,
                                                                  next_state,
                                                                  "ϵ",
                                                                  index,
                                                                  epsilon_set))

            # explore non-epsilon transitions if input tape is not empty
            if this_config.tape:
                new_tape = this_config.tape[1:]
                symbol = this_config.tape[0]

                # check if a transition function exists for the current state and symbol
                if symbol in self.transitions[this_config.state]:
                    for next_state in self.transitions[this_config.state][symbol]:
                        new_configurations.append(FAConfiguration(new_tape, next_state, symbol, index))

        # if no new states are possible and no accepting state has been reached,
        # end computation and mark non-acceptance
        if not new_configurations:
            self.complete = True
            self.accepted = False
            return True
        else:
            self.computation_history.append(new_configurations)
            self.current_configurations = new_configurations

    def simulate_util_completion(self):
        while not self.simulate_one_step():
            pass




