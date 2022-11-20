import os
import pyfiglet
import tests as tests

INVALID_OUT = "Wrong Input!"

def test_any(test):
    test.test_any()


def test_coord(test):
    test.test_coord()


def test_both(test):
    test.test_both()


def run():

    os.system("cls")
    print(pyfiglet.figlet_format("TEST", font = "digital"))

    algorithm = True    # bully
    nodes = 4

    while True:
        try:
            op = int(input("1. Generic node Failure\n2. Coordinator Failure\n3. Two nodes' Failure (including the coordinator)\n4. Change Algorithm (Bully by default)\n5. Change number of nodes (DEFAULT = 4)\n6. Exit\n\n"))
        except ValueError:
            print(INVALID_OUT)
            continue
        except KeyboardInterrupt:
            return

        if op not in [1, 2, 3, 4, 5, 6]:
            print(INVALID_OUT)
            continue

        if op == 4:
            algorithm = not(algorithm)
            if algorithm:
                print("\nChang and Roberts -> Bully\n")
            else:
                print("\nBully -> Chang and Roberts\n")
            continue

        if op == 5:
            nodes = int(input("Enter new number of nodes:\n"))
            if nodes < 4:
                print("Error: invalid number of nodes! (must be 4 or more)\nIt's going to be set equal to 4\n")
                nodes = 4
            continue

        if op == 6:
            return

        command = {1: test_any, 2: test_coord, 3: test_both}

        test = tests.Tests(nodes, algorithm)
        command[op](test)
        return


if __name__ == '__main__':
    run()
