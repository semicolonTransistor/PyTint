import argparse
from typing import List
from pytint.machine_io import load_machine_from_file, UnsupportedMachine, IncompleteMachine
from pytint.visualization import render_finite_automaton, render_finite_automaton_history


def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("machine_file", help="File containing definitions for the machine")
    parser.add_argument("test_file", help="File containing test cases to be used with the machine", nargs="?")
    parser.add_argument("-m", "--machine-type", choices=["dfa", "nfa"], default="",  help="Type of the machine")
    parser.add_argument("-n", "--name", default=None, help="Name of the machine")
    parser.add_argument("-t", "--test-case", default=None, help="Single test case to use in lieu of a test file")
    parser.add_argument("-s", "--state-diagram", default=None, const="",  nargs="?",
                        help="Renders a state diagram, optionally specify a file to save it to")
    parser.add_argument("-p", "--path-graphs", default=None, const="", nargs="?",
                        help="Renders a path graph for each input, optionally specify a directory to store all them.")
    arguments = parser.parse_args()

    # load machine
    try:
        machine = load_machine_from_file(arguments.machine_file, arguments.machine_type)
    except FileNotFoundError:
        print("Error loading Machine: Machine file \"{}\" does not exist!".format(arguments.machine_file))
        exit(-1)
        return

    except (IncompleteMachine, UnsupportedMachine) as e:
        print("Error loading machine: {}".format(e))
        exit(-1)
        return

    # rename machine if necessary
    if arguments.name is not None:
        machine.name = arguments.name

    # render state diagram if requested
    state_diagram_path: str = machine.name

    if arguments.state_diagram is not None:
        if arguments.state_diagram:
            state_diagram_path = arguments.state_diagram
        render_finite_automaton(machine).render(state_diagram_path, cleanup=True)

    # setting up test cases
    tests: List[List[str]] = list()
    if arguments.test_case is not None:
        tests.append(arguments.test_case.split(" "))
    elif arguments.test_file is not None:
        try:
            with open(arguments.test_file, "r") as test_file:
                test_lines = test_file.readlines()
                for test_line in test_lines:
                    test_line = test_line.strip()
                    test_symbols = test_line.split(" ")
                    tests.append(list(filter(None, test_symbols)))
        except FileNotFoundError:
            print("Error loading tests: Test file {} does not exist!".format(arguments.test_file))
        except OSError:
            print("Error loading tests: Unable to access {}!".format(arguments.test_file))

    # set up path graphs
    draw_path_graphs = False
    path_graph_dir = None

    if arguments.path_graphs is not None:
        draw_path_graphs = True
        if arguments.path_graphs:
            path_graph_dir = arguments.path_graphs

    # if there are tests to run, run them
    for test in tests:
        machine.start_new_computation(test)
        machine.simulate_util_completion()
        if machine.accepted:
            result_text = "accepted"
        else:
            result_text = "rejected"
        print("Input {} is {}".format(" ".join(test), result_text))

        # render path graphs
        if draw_path_graphs:
            render_finite_automaton_history(machine).render(machine.name+" - " + " ".join(test),
                                                            directory=path_graph_dir, cleanup=True)


if __name__ == "__main__":
    main()
