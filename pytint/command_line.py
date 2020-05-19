import argparse
from typing import List
from pytint.machine_io import load_nfa, load_dfa

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("machine_file", help="File containing definitions for the machine")
    parser.add_argument("test_file", help="File containing test cases to be used with the machine", nargs="?")
    parser.add_argument("-m", "--machine-type", choices=["dfa", "nfa"], default="dfa",  help="Type of the machine")
    parser.add_argument("-t", "--test-case", default=None, help="Single test case to use in lieu of a test file")
    arguments = parser.parse_args()

    # load machine
    try:
        if arguments.machine_type == "dfa":
            machine = load_dfa(arguments.machine_file)
        elif arguments.machine_type == "nfa":
            machine = load_nfa(arguments.machine_file)
        else:
            print("Unsupported machine type, exiting")
            exit(-1)
    except FileNotFoundError:
        print("Machine file \"{}\" does not exist!".format(arguments.machine_file))
        exit(-2)

    # setting up test cases
    tests: List[List[str]] = list()
    if arguments.test_case is not None:
        tests.append(arguments.test_case.split(" "))
    elif arguments.test_file is not None:
        with open(arguments.test_file, "r") as test_file:
            test_lines = test_file.readlines()
            for test_line in test_lines:
                test_line = test_line.strip()
                test_symbols = test_line.split(" ")
                if test_symbols:  # add to tests if none empty
                    tests.append(test_symbols)

    # if there are tests to run, run them
    for test in tests:
        result, path = machine.process(test)
        if result:
            result_text = "accepted"
        else:
            result_text = "rejected"
        print("Input {} is {}".format(test, result_text))


if __name__ == "__main__":
    main()
