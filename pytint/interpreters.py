from typing import Dict, Tuple, List, Union, Iterable, Deque, Set
from collections import deque
import logging

DeterministicTransitions = Dict[str, Dict[str, str]]
NonDeterministicTransitions = Dict[str, Dict[str, Iterable[str]]]

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


class DeterministicFiniteAutomaton:
    def __init__(self, transitions: DeterministicTransitions, start: str, accepting: Iterable[str], name: str = ""):
        self.transitions: DeterministicTransitions = transitions
        self.start: str = start
        self.accepting: Tuple[str, ...] = tuple(accepting)
        self.name = name

    def process(self, word: Iterable[str]) -> Tuple[bool, Path]:
        return self.__process(deque(word), self.start)

    def __process(self, word: Deque[str], state: str) -> Tuple[bool, Path]:
        if word:
            # if word is not empty, process it
            symbol = word.popleft()  # pop off the first symbol in the word

            if state in self.transitions and symbol in self.transitions.get(state):
                # follow transition function and recursively process the rest of the word.
                result, path = self.__process(word, self.transitions.get(state).get(symbol))
                path = (state, [(symbol, path)])
                return result, path
            else:
                # Missing transition function
                exception = MissingTransitionFunction(state, symbol, word)  # construct an exception
                fa_logger.error(str(exception))  # log the problem
                raise exception  # raise the exception
        else:
            # end of input reached, just check if the final state is accepting
            return state in self.accepting, state


class NonDeterministicFiniteAutomaton:
    def __init__(self, transitions: NonDeterministicTransitions, start: str, accepting: Iterable[str], name: str = ""):
        self.transitions: NonDeterministicTransitions = transitions
        self.start: str = start
        self.accepting: Iterable[str] = tuple(accepting)
        self.name = name

    def process(self, word: Iterable[str]):
        return self.__process(deque(word), self.start, set())

    def __process(self, word: Deque[str], state: str, epsilon_set: Set[str]) -> Tuple[bool, Path]:
        # print("word: {}, state: {}, epsilon set: {}".format(word, state, epsilon_set))

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

                for next_state in non_epsilon_next_states:
                    rest_result, rest_path = self.__process(word_rest.copy(), next_state, set())
                    rest_paths.append((symbol, rest_path))
                    rest_results.append(rest_result)

        if state in self.transitions and "ε" in self.transitions[state]:
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


FiniteAutomaton = Union[DeterministicFiniteAutomaton, NonDeterministicFiniteAutomaton]