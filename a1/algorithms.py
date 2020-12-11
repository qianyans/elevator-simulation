"""CSC148 Assignment 1 - Algorithms

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===

This file contains two sets of algorithms: ones for generating new arrivals to
the simulation, and ones for making decisions about how elevators should move.

As with other files, you may not change any of the public behaviour (attributes,
methods) given in the starter code, but you can definitely add new attributes
and methods to complete your work here.

See the 'Arrival generation algorithms' and 'Elevator moving algorithms'
sections of the assignment handout for a complete description of each algorithm
you are expected to implement in this file.
"""
import csv
from enum import Enum
import random
from typing import Dict, List, Optional

from entities import Person, Elevator


###############################################################################
# Arrival generation algorithms
###############################################################################
class ArrivalGenerator:
    """An algorithm for specifying arrivals at each round of the simulation.

    === Attributes ===
    max_floor: The maximum floor number for the building.
               Generated people should not have a starting or target floor
               beyond this floor.
    num_people: The number of people to generate, or None if this is left
                up to the algorithm itself.

    === Representation Invariants ===
    max_floor >= 2
    num_people is None or num_people >= 0
    """
    max_floor: int
    num_people: Optional[int]

    def __init__(self, max_floor: int, num_people: Optional[int]) -> None:
        """Initialize a new ArrivalGenerator.

        Preconditions:
            max_floor >= 2
            num_people is None or num_people >= 0
        """
        self.max_floor = max_floor
        self.num_people = num_people

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """Return the new arrivals for the simulation at the given round.

        The returned dictionary maps floor number to the people who
        arrived starting at that floor.

        You can choose whether to include floors where no people arrived.
        """
        raise NotImplementedError


class RandomArrivals(ArrivalGenerator):
    """Generate a fixed number of random people each round.

    Generate 0 people if self.num_people is None.

    For our testing purposes, this class *must* have the same initializer header
    as ArrivalGenerator. So if you choose to to override the initializer, make
    sure to keep the header the same!

    Hint: look up the 'sample' function from random.
    """

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """Return the new arrivals for the simulation at the given round.
        The starting floor and target floor of the new arrivals are random.

        The returned dictionary maps floor number to the people who
        arrived starting at that floor.
        """
        list_of_people = []
        floor_to_people = {}

        for i in range(1, self.max_floor + 1):
            floor_to_people[i] = []

        if self.num_people:
            for i in range(self.num_people):
                start_floor = random.randint(1, self.max_floor)
                target_floor = random.randint(1, self.max_floor)
                while start_floor == target_floor:
                    target_floor = random.randint(1, self.max_floor)

                new_person = Person(start_floor, target_floor)
                list_of_people.append(new_person)

            for person in list_of_people:
                floor_to_people[person.start].append(person)

        return floor_to_people


class FileArrivals(ArrivalGenerator):
    """Generate arrivals from a CSV file.

    round_to_people:
        Stores the starting floor and target floor of the arrivals
        for a given round number.
    """
    round_to_people: Dict[int, List[List[int]]]

    def __init__(self, max_floor: int, filename: str) -> None:
        """Initialize a new FileArrivals algorithm from the given file.

        The num_people attribute of every FileArrivals instance is set to None,
        since the number of arrivals depends on the given file.

        Precondition:
            <filename> refers to a valid CSV file, following the specified
            format and restrictions from the assignment handout.
        """
        ArrivalGenerator.__init__(self, max_floor, None)

        # We've provided some of the "reading from csv files" boilerplate code
        # for you to help you get started.
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)

            self.round_to_people = {}

            for line in reader:
                round_num = int(line.pop(0))
                self.round_to_people[round_num] = []
                while line:
                    start_and_target = []
                    start_and_target.extend([int(line.pop(0)),
                                             int(line.pop(0))])
                    self.round_to_people[round_num].append(start_and_target)
                    # {1: [[1, 2], [5, 6]], 3: [[4, 2]]}

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """Return the new arrivals for the simulation at the given round.

        The returned dictionary maps floor number to the people who
        arrived starting at that floor.
        """
        list_of_people = []
        floor_to_people = {}

        for i in range(1, self.max_floor + 1):
            floor_to_people[i] = []

        for l in self.round_to_people.get(round_num, []):
            new_person = Person(l[0], l[1])
            list_of_people.append(new_person)

        for person in list_of_people:
            floor_to_people[person.start].append(person)

        return floor_to_people


###############################################################################
# Elevator moving algorithms
###############################################################################
class Direction(Enum):
    """
    The following defines the possible directions an elevator can move.
    This is output by the simulation's algorithms.

    The possible values you'll use in your Python code are:
        Direction.UP, Direction.DOWN, Direction.STAY
    """
    UP = 1
    STAY = 0
    DOWN = -1


class MovingAlgorithm:
    """An algorithm to make decisions for moving an elevator at each round.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """Return a list of directions for each elevator to move to.

        As input, this method receives the list of elevators in the simulation,
        a dictionary mapping floor number to a list of people waiting on
        that floor, and the maximum floor number in the simulation.

        Note that each returned direction should be valid:
            - An elevator at Floor 1 cannot move down.
            - An elevator at the top floor cannot move up.
        """
        raise NotImplementedError

    def get_start_floor_list(self,
                             waiting: Dict[int, List[Person]]) -> List[int]:
        """Return a list of starting floor of Person in <waiting>.
        """
        start_list = []
        for floor in waiting:
            waiting_list = waiting[floor]
            for person in waiting_list:
                start_list.append(person.get_start_floor())

        return start_list


class RandomAlgorithm(MovingAlgorithm):
    """A moving algorithm that picks a random direction for each elevator.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        three_direct = [Direction.UP, Direction.DOWN, Direction.STAY]
        first_floor_direct = [Direction.UP, Direction.STAY]
        max_floor_direct = [Direction.DOWN, Direction.STAY]

        direct_list = []

        for elevator in elevators:
            if elevator.get_current_floor() == 1:
                direct_list.extend(random.choices(first_floor_direct, k=1))
            elif elevator.get_current_floor() == max_floor:
                direct_list.extend(random.choices(max_floor_direct, k=1))
            else:
                direct_list.extend(random.choices(three_direct, k=1))

        return direct_list


class PushyPassenger(MovingAlgorithm):
    """A moving algorithm that preferences the first passenger on each elevator.

    If the elevator is empty, it moves towards the *lowest* floor that has at
    least one person waiting, or stays still if there are no people waiting.

    If the elevator isn't empty, it moves towards the target floor of the
    *first* passenger who boarded the elevator.
    """

    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        direct_list = []
        for elevator in elevators:
            current_floor = elevator.get_current_floor()
            if len(elevator.passengers) == 0:
                waiting_list_all = MovingAlgorithm.get_start_floor_list(self,
                                                                        waiting)
                if len(waiting_list_all) == 0:
                    direct_list.append(Direction.STAY)
                else:
                    direction = (Direction.UP if current_floor <
                                 min(waiting_list_all)
                                 else Direction.DOWN)
                    direct_list.append(direction)
            else:
                passenger_list = elevator.get_passengers()
                target = passenger_list[0].get_target_floor()
                direction = (Direction.UP if current_floor < target
                             else Direction.DOWN)
                direct_list.append(direction)

        return direct_list


class ShortSighted(MovingAlgorithm):
    """A moving algorithm that preferences the closest possible choice.

    If the elevator is empty, it moves towards the *closest* floor that has at
    least one person waiting, or stays still if there are no people waiting.

    If the elevator isn't empty, it moves towards the closest target floor of
    all passengers who are on the elevator.

    In this case, the order in which people boarded does *not* matter.
    """

    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        # TODO: Docstring
        direct_list = []
        # get_start_floor_list(self, waiting: Dict[int, List[Person]])
        for elevator in elevators:
            current_floor = elevator.get_current_floor()
            if len(elevator.passengers) == 0:
                waiting_list_all = MovingAlgorithm.get_start_floor_list(self,
                                                                        waiting)
                if len(waiting_list_all) == 0:
                    direct_list.append(Direction.STAY)
                else:
                    direction = self._to_closest_floor(waiting_list_all,
                                                       current_floor)
                    direct_list.append(direction)
            else:
                passenger_list = elevator.get_passengers()
                target_floor_list = self._get_target_floor_list(passenger_list)
                direction = self._to_closest_floor(target_floor_list,
                                                   current_floor)
                direct_list.append(direction)

        return direct_list

    def _to_closest_floor(self, list_of_floor: List[int],
                          current_floor: int) -> Direction:
        floor_list_copy = list_of_floor.copy()
        floor_list_copy.append(current_floor)
        floor_list_copy.sort()
        current_floor_index = floor_list_copy.index(current_floor)
        if current_floor_index == 0:
            return Direction.UP
        elif current_floor_index == len(floor_list_copy) - 1:
            return Direction.DOWN
        else:
            lower_closest = floor_list_copy[current_floor_index - 1]
            higher_closest = floor_list_copy[current_floor_index + 1]
            if current_floor - lower_closest > (higher_closest -
                                                current_floor):
                return Direction.UP
            else:
                return Direction.DOWN

    def _get_target_floor_list(self, passenger_list: List[Person]) -> List[int]:
        target_floor = []
        for person in passenger_list:
            target_floor.append(person.get_target_floor())

        return target_floor


if __name__ == '__main__':
    # Don't forget to check your work regularly with python_ta!
    import python_ta
    python_ta.check_all(config={
        'allowed-io': ['__init__'],
        'extra-imports': ['entities', 'random', 'csv', 'enum'],
        'max-nested-blocks': 4,
        'disable': ['R0201']
    })
