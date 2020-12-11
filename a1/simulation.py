"""CSC148 Assignment 1 - Simulation

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module description ===
This contains the main Simulation class that is actually responsible for
creating and running the simulation. You'll also find the function `sample_run`
here at the bottom of the file, which you can use as a starting point to run
your simulation on a small configuration.

Note that we have provided a fairly comprehensive list of attributes for
Simulation already. You may add your own *private* attributes, but should not
remove any of the existing attributes.
"""
# You may import more things from these modules (e.g., additional types from
# typing), but you may not import from any other modules.
from typing import Dict, List, Any

import algorithms
from entities import Person, Elevator
from visualizer import Visualizer


class Simulation:
    """The main simulation class.

    === Attributes ===
    arrival_generator: the algorithm used to generate new arrivals.
    elevators: a list of the elevators in the simulation
    moving_algorithm: the algorithm used to decide how to move elevators
    num_floors: the number of floors
    visualizer: the Pygame visualizer used to visualize this simulation
    waiting: a dictionary of people waiting for an elevator
             (keys are floor numbers, values are the list of waiting people)
    num_round: the number of simulation rounds
    total_people: the total number of persons generated during this simulation
    people_completed: a list of people arriving target floor
    """
    arrival_generator: algorithms.ArrivalGenerator
    elevators: List[Elevator]
    moving_algorithm: algorithms.MovingAlgorithm
    num_floors: int
    visualizer: Visualizer
    waiting: Dict[int, List[Person]]
    num_round: int
    total_people: int
    people_completed: List[Person]

    def __init__(self,
                 config: Dict[str, Any]) -> None:
        """Initialize a new simulation using the given configuration."""
        """
        config = {
        'num_people_per_round': 2,
    }
        """
        self.arrival_generator = config['arrival_generator']

        self.elevators = []
        for i in range(config['num_elevators']):
            new_elevator = Elevator(config['elevator_capacity'])
            self.elevators.append(new_elevator)

        self.moving_algorithm = config['moving_algorithm']

        self.num_floors = config['num_floors']

        self.waiting = {}
        for i in range(1, config['num_floors'] + 1):
            self.waiting[i] = []

        # Initialize the visualizer.
        # Note that this should be called *after* the other attributes
        # have been initialized.
        self.visualizer = Visualizer(self.elevators,
                                     self.num_floors,
                                     config['visualize'])
        self.num_round = 0
        self.total_people = 0
        self.people_completed = []

    ############################################################################
    # Handle rounds of simulation.
    ############################################################################
    def run(self, num_rounds: int) -> Dict[str, Any]:
        """Run the simulation for the given number of rounds.

        Return a set of statistics for this simulation run, as specified in the
        assignment handout.

        Precondition: num_rounds >= 1.

        Note: each run of the simulation starts from the same initial state
        (no people, all elevators are empty and start at floor 1).
        """
        for i in range(num_rounds):
            self.visualizer.render_header(i)

            # Stage 1: generate new arrivals
            self._generate_arrivals(i)

            # Stage 2: leave elevators
            self._handle_leaving()

            # Stage 3: board elevators
            self._handle_boarding()

            # Stage 4: move the elevators using the moving algorithm
            self._move_elevators()

            # Pause for 1 second
            self.visualizer.wait(1)

        return self._calculate_stats()

    def _generate_arrivals(self, round_num: int) -> None:
        """Generate and visualize new arrivals."""
        floor_to_arrivals = self.arrival_generator.generate(round_num)

        for floor in floor_to_arrivals:
            arrivals = floor_to_arrivals[floor]
            self.total_people += len(arrivals)
            self.waiting[floor].extend(arrivals)

        Visualizer.show_arrivals(self.visualizer, floor_to_arrivals)

    def _handle_leaving(self) -> None:
        """Handle people leaving elevators."""
        for elevator in self.elevators:
            passenger_list = elevator.get_passengers()

            i = 0
            while i < len(passenger_list):
                passenger = passenger_list[i]
                if passenger.get_target_floor() == elevator.get_current_floor():
                    self.people_completed.append(passenger)
                    elevator.person_disembark(passenger)
                    Visualizer.show_disembarking(self.visualizer,
                                                 passenger, elevator)
                else:
                    i += 1

    def _handle_boarding(self) -> None:
        """Handle boarding of people and visualize."""
        """
        arrival_generator: algorithms.ArrivalGenerator
        elevators: List[Elevator]
        moving_algorithm: algorithms.MovingAlgorithm
        num_floors: int
        visualizer: Visualizer
        waiting: Dict[int, List[Person]]
        """
        for elevator in self.elevators:
            while len(elevator.passengers) < elevator.max_capacity:
                waiting_list = self.waiting[elevator.current_floor]
                if len(waiting_list) != 0:
                    wait_max = waiting_list.pop(0)
                    elevator.passengers.append(wait_max)
                    Visualizer.show_boarding(self.visualizer, wait_max,
                                             elevator)
                else:
                    break

        self.num_round += 1
        self._increase_wait_time()

    def _increase_wait_time(self) -> None:
        """Increase wait time for people who is waiting for the elevator and
        who is travelling on the elevator.
        """
        # increase wait_time for people waiting
        for floor in self.waiting:
            wait_list = self.waiting[floor]
            for person in wait_list:
                person.wait()

        # increase wait_time for people travelling
        for elevator in self.elevators:
            for person in elevator.get_passengers():
                person.wait()

    def _move_elevators(self) -> None:
        """Move the elevators in this simulation.

        Use this simulation's moving algorithm to move the elevators.
        """
        direction_list = self.moving_algorithm.move_elevators(self.elevators,
                                                              self.waiting,
                                                              self.num_floors)
        for i in range(len(direction_list)):
            self.elevators[i].set_current_floor(direction_list[i].value)

        Visualizer.show_elevator_moves(self.visualizer, self.elevators,
                                       direction_list)

    ############################################################################
    # Statistics calculations
    ############################################################################
    def _calculate_stats(self) -> Dict[str, int]:
        """Report the statistics for the current run of this simulation.
        """
        wait_time_of_completed = []
        for person in self.people_completed:
            wait_time_of_completed.append(person.get_wait_time())

        if len(self.people_completed) != 0:
            max_time = max(wait_time_of_completed)
            min_time = min(wait_time_of_completed)
            avg_time = round(sum(wait_time_of_completed) /
                             len(wait_time_of_completed))
        else:
            max_time = -1
            min_time = -1
            avg_time = -1

        return {
            'num_iterations': self.num_round,
            'total_people': self.total_people,
            'people_completed': len(self.people_completed),
            'max_time': max_time,
            'min_time': min_time,
            'avg_time': avg_time
        }


def sample_run() -> Dict[str, int]:
    """Run a sample simulation, and return the simulation statistics."""
    config = {
        'num_floors': 5,
        'num_elevators': 1,
        'elevator_capacity': 4,
        # This is likely not used.
        'num_people_per_round': 2,
        'arrival_generator': algorithms.FileArrivals(5, 'arr.csv'),
        'moving_algorithm': algorithms.PushyPassenger(),
        'visualize': True
    }
    sim = Simulation(config)
    results = sim.run(17)
    return results


if __name__ == '__main__':
    # Uncomment this line to run our sample simulation (and print the
    # statistics generated by the simulation).
    print(sample_run())

    # import python_ta
    # python_ta.check_all(config={
    #     'extra-imports': ['entities', 'visualizer', 'algorithms', 'time'],
    #     'max-nested-blocks': 4,
    #     'max-attributes': 12,
    #     'disable': ['R0201']
    # })
