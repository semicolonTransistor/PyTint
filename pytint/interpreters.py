from typing import Dict, Tuple, List, Union, Iterable, Deque, Set
from collections import deque
import logging

DeterministicTransitions = Dict[str, Dict[str, str]]
NonDeterministicTransitions = Dict[str, Dict[str, Iterable[str]]]
Transitions = Dict[str, Dict[str, Union[str, Iterable[str]]]]

Path = Union[str, Tuple[str, List[Tuple[str, "Path"]]]]

fa_logger = logging.getLogger(__name__)


# exceptions
class MissingTransitionFunction(Exception):
    """Exception Raised when no transition function is defined for the current state
    and input symbol."""

    def __init__(self, state: str, symbol: str, rest: Iterable):
        self.state = state
        self.symbol = symbol
        self.rest = rest

    def __str__(self):
        return ("Unable to find transition function "
                "for state \"{state}\" and symbol \"{symbol}\" "
                "whilst processing word {word}").format(state=self.state,
                                                        symbol=self.symbol,
                                                        word=[self.symbol] + list(self.rest))


class MultipleTransitions(Exception):
    """Exception raised when multiple transitions are defined for a single state input pair whilst in dfa mode"""

    def __init__(self, state: str, symbol: str, rest: Iterable):
        self.state = state
        self.symbol = symbol
        self.rest = rest

    def __str__(self):
        return ("Multiple transitions"
                "for state \"{state}\" and symbol \"{symbol}\" "
                "whilst processing word {word}").format(state=self.state,
                                                        symbol=self.symbol,
                                                        word=[self.symbol] + list(self.rest))


# finite automatons
class FiniteAutomaton:
    def __init__(self, transitions: Transitions, start: str, accepting: Iterable[str],
                 name: str = "", deterministic: bool = False):
        for state in transitions:
            for symbol in transitions[state]:
                next_state = transitions[state][symbol]
                if isinstance(next_state, str):
                    transitions[state][symbol] = [next_state]

        self.transitions = transitions
        self.start: str = start
        self.accepting: Iterable[str] = tuple(accepting)
        self.name = name
        self.deterministic = deterministic

    def process(self, word: Iterable[str]):
        fa_logger.info("Testing input {}", " ".join(word))
        return self.__process(deque(word), self.start, set())

    def __process(self, word: Deque[str], state: str, epsilon_set: Set[str]) -> Tuple[bool, Path]:
        fa_logger.info("{}:{}", state, " ".join(word))

        # prevents epsilon loop
        if state in epsilon_set:
            return False, state

        rest_paths = list()
        rest_results = list()
        non_epsilon_next_states = set()

        if word:
            # if word is not empty, process it
            word_rest = word.copy()
            symbol = word_rest.popleft()  # pop off the first symbol in the word

            if state in self.transitions and symbol in self.transitions[state]:  # transition exists
                # follow transition function and recursively process the rest of the word.
                non_epsilon_next_states.update(self.transitions[state][symbol])

                if self.deterministic:
                    if len(non_epsilon_next_states) == 0:
                        # if transition function is empty for some reason
                        exception = MissingTransitionFunction(state, symbol, word)  # construct an exception
                        fa_logger.error(str(exception))  # log the problem
                        raise exception  # raise the exception
                    elif len(non_epsilon_next_states) > 1:
                        # if multiple transitions defined for a single state symbol pair(not allowed in nfa)
                        exception = MultipleTransitions(state, symbol, word)
                        fa_logger.error(str(exception))
                        raise exception

                for next_state in non_epsilon_next_states:
                    rest_result, rest_path = self.__process(word_rest.copy(), next_state, set())
                    rest_paths.append((symbol, rest_path))
                    rest_results.append(rest_result)
            elif self.deterministic:
                # Missing transition in deterministic mode
                exception = MissingTransitionFunction(state, symbol, word)  # construct an exception
                fa_logger.error(str(exception))  # log the problem
                raise exception  # raise the exception

        # only process epsilons if machine is non-deterministic
        if not self.deterministic and state in self.transitions and "ε" in self.transitions[state]:
            # process epsilon transition
            epsilon_next_states = set(self.transitions[state]["ε"])
            epsilon_next_states -= non_epsilon_next_states  # remove explored states
            epsilon_set.add(state)

            for next_state in epsilon_next_states:
                rest_result, rest_path = self.__process(word.copy(), next_state, epsilon_set.copy())
                rest_paths.append(("ε", rest_path))
                rest_results.append(rest_result)

        if word:
            if rest_results:  # if at least 1 transition available
                return any(rest_results), (state, rest_paths)
            else:  # dead end
                return False, state

        else:  # word fully consumed, check if final state is accepting
            if state in self.accepting:
                return True, state
            elif rest_results:  # if not check if there are other paths
                return any(rest_results), (state, rest_paths)
            else:
                return False, state


class DeterministicFiniteAutomaton(FiniteAutomaton):
    def __init__(self, transitions: DeterministicTransitions, start: str, accepting: Iterable[str], name: str = ""):
        super().__init__(transitions, start, accepting, name, True)


class NonDeterministicFiniteAutomaton(FiniteAutomaton):
    def __init__(self, transitions: NonDeterministicTransitions, start: str, accepting: Iterable[str], name: str = ""):
        super().__init__(transitions, start, accepting, name, False)


