"""CSC148 Assignment 1 - People and Elevators

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module description ===
This module contains classes for the two "basic" entities in this simulation:
people and elevators. We have provided basic outlines of these two classes
for you; you are responsible for implementing these two classes so that they
work with the rest of the simulation.

You may NOT change any existing attributes, or the interface for any public
methods we have provided. However, you can (and should) add new attributes,
and of course you'll have to implement the methods we've provided, as well
as add your own methods to complete this assignment.

Finally, note that Person and Elevator each inherit from a kind of sprite found
in sprites.py; this is to enable their instances to be visualized properly.
You may not change sprites.py, but are responsible for reading the documentation
to understand these classes, as well as the abstract methods your classes must
implement.
"""
from __future__ import annotations
from typing import List
from sprites import PersonSprite, ElevatorSprite


class Elevator(ElevatorSprite):
    """An elevator in the elevator simulation.

    Remember to add additional documentation to this class docstring
    as you add new attributes (and representation invariants).

    === Attributes ===
    passengers: A list of the people currently on this elevator
    max_capacity: The maximum number of people that can board on this elevator
    current_floor: The current floor that this elevator is at.
    === Representation invariants ===
    max_capacity >= 1

    """
    passengers: List[Person]
    max_capacity: int
    current_floor: int

    def __init__(self, max_capacity: int) -> None:
        """
        Initialize a new elevator.

        Precondition: max_capacity >= 1
        """
        ElevatorSprite.__init__(self)
        self.max_capacity = max_capacity
        self.passengers = []
        self.current_floor = 1

    def fullness(self) -> float:
        """Return the fraction that this elevator is filled.

        The value returned should be a float between 0.0 (completely empty) and
        1.0 (completely full).
        """
        return len(self.passengers) / self.max_capacity

    def get_passengers(self) -> List[Person]:
        """Return the list of Person who is in this elevator.
        """
        return self.passengers

    def get_current_floor(self) -> int:
        """Return the current floor of this elevator.
        """
        return self.current_floor

    def set_current_floor(self, move: int) -> None:
        """Change the current floor of this elevator to another floor <move>.
        """
        self.current_floor += move

    def person_disembark(self, person: Person) -> None:
        """Remove this person <person> from the passenger list of this elevator.
        """
        self.passengers.remove(person)


class Person(PersonSprite):
    """A person in the elevator simulation.

    === Attributes ===
    start: the floor this person started on
    target: the floor this person wants to go to
    wait_time: the number of rounds this person has been waiting

    === Representation invariants ===
    start >= 1
    target >= 1
    wait_time >= 0
    """
    start: int
    target: int
    wait_time: int

    def __init__(self, start: int, target: int) -> None:
        """
        Initialize a person who takes elevator.
        """
        self.start = start
        self.target = target
        self.wait_time = 0
        PersonSprite.__init__(self)

    def wait(self) -> None:
        """
        Increase this person's wait time (for each round).
        """
        self.wait_time += 1

    def get_anger_level(self) -> int:
        """Return this person's anger level.

        A person's anger level is based on how long they have been waiting
        before reaching their target floor.
            - Level 0: waiting 0-2 rounds
            - Level 1: waiting 3-4 rounds
            - Level 2: waiting 5-6 rounds
            - Level 3: waiting 7-8 rounds
            - Level 4: waiting >= 9 rounds
        """
        if 0 <= self.wait_time <= 2:
            return 0
        elif 3 <= self.wait_time <= 4:
            return 1
        elif 5 <= self.wait_time <= 6:
            return 2
        elif 7 <= self.wait_time <= 8:
            return 3
        else:
            return 4

    def get_target_floor(self) -> int:
        """Return the target floor of this Person.
        """
        return self.target

    def get_start_floor(self) -> int:
        """Return the starting floor of this Person.
        """
        return self.start

    def get_wait_time(self) -> int:
        """Return the wait time of this person.
        """
        return self.wait_time


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['sprites'],
        'max-nested-blocks': 4
    })
