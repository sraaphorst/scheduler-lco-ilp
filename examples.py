# examples.py
# By Sebastian Raaphorst, 2020.

# Alternate between CBC and Gurobi by switching the following imports:
from cbc_solver import *
# from gurobi_solver import *


def example_fully_scheduled(schedule: Scheduler) -> None:
    """
    A small example which will schedule fully all observations.
    """
    print("*** FULLY SCHEDULED ***")

    # Create the timeslots.
    # GN: 0 1 2 3  4  5
    # GS: 6 7 8 9 10 11
    timeslots = TimeSlots()

    # Create the list of observations. We will be working with the index of observation in this list.
    observations = Observations()

    # Observation 0
    observations.add_obs('3', [TS(0), TS(1), TS(2), TS(5), TS(6), TS(9)], 300)

    # Observation 1
    observations.add_obs('2', [TS(0), TS(3), TS(8)], 900)

    # Observation 2
    observations.add_obs('3', [TS(1), TS(3), TS(4), TS(8), TS(10)], 600)

    # Observation 3
    observations.add_obs('1', [TS(0), TS(3), TS(6), TS(9), TS(11)], 300)

    # Observation 4
    observations.add_obs('2', [TS(1), TS(3), TS(7), TS(9)], 900)

    # Observation 5
    observations.add_obs('1', [TS(3), TS(8), TS(10)], 600)

    observations.calculate_priority()
    print_observations(observations, timeslots)

    # Run the solver.
    print(f'\nScheduling {timeslots.num_timeslots_per_site * timeslots.timeslot_length} s per site...')
    final_schedule, final_score = schedule(timeslots, observations)
    print('Scheduling done.\n')

    print_schedule(timeslots, observations, final_schedule, final_score)


def example_underscheduled(schedule: Scheduler) -> None:
    """
    A small example which will schedule fully all observations and have room left over.
    One of the observations has slack time of 100 s, i.e. observation 1.
    """
    print("*** UNDER-SCHEDULED ***")

    # Create the timeslots.
    # GN: 0 1 2 3  4  5
    # GS: 6 7 8 9 10 11
    timeslots = TimeSlots()

    # Create the list of observations. We will be working with the index of observation in this list.
    observations = Observations()

    # Observation 0
    observations.add_obs('2', [TS(0), TS(7), TS(9)], 800)

    # Observation 1
    observations.add_obs('1', [TS(0), TS(2), TS(4)], 600)

    # Observation 2
    observations.add_obs('1', [TS(3)], 900)

    # Observation 3
    observations.add_obs('3', [TS(2), TS(5), TS(6), TS(10)], 300)

    # Observation 4
    observations.add_obs('3', [TS(1), TS(3), TS(5), TS(6), TS(10)], 300)

    observations.calculate_priority()
    print_observations(observations, timeslots)

    # Run the solver.
    print(f'\nScheduling {timeslots.num_timeslots_per_site * timeslots.timeslot_length} s per site...')
    final_schedule, final_score = schedule(timeslots, observations)
    print('Scheduling done.\n')

    print_schedule(timeslots, observations, final_schedule, final_score)


def example_overscheduled(schedule: Scheduler) -> None:
    """
    A small example which will cannot fully schedule all observations as there is insufficient time.
    """
    print("*** OVER-SCHEDULED ***")

    # Create the timeslots.
    # GN: 0 1 2 3  4  5
    # GS: 6 7 8 9 10 11
    timeslots = TimeSlots()

    # Create the list of observations. We will be working with the index of observation in this list.
    observations = Observations()

    # Observation 0
    observations.add_obs('1', [TS(0), TS(1), TS(3), TS(6), TS(7), TS(8), TS(9)], 900)

    # Observation 1
    observations.add_obs('2', [TS(1), TS(3), TS(7), TS(8)], 900)

    # Observation 2
    observations.add_obs('2', [TS(1), TS(2), TS(3), TS(4), TS(6), TS(8), TS(9), TS(10)], 600)

    # Observation 3
    observations.add_obs('1', [TS(0), TS(2), TS(6), TS(7), TS(8)], 1200)

    # Observation 4
    observations.add_obs('3', [TS(0), TS(1), TS(2), TS(3), TS(4), TS(5),
                               TS(6), TS(7), TS(8), TS(9), TS(10), TS(11)], 300)

    # Observation 5
    observations.add_obs('3', [TS(0), TS(1), TS(2), TS(3), TS(4), TS(5),
                               TS(6), TS(7), TS(8), TS(9), TS(10), TS(11)], 300)

    observations.calculate_priority()
    print_observations(observations, timeslots)

    # Run the solver.
    print(f'\nScheduling {timeslots.num_timeslots_per_site * timeslots.timeslot_length} s per site...')
    final_schedule, final_score = schedule(timeslots, observations)
    print('Scheduling done.\n')

    print_schedule(timeslots, observations, final_schedule, final_score)


def example_do_not_fit(schedule: Scheduler[None]):
    """
    A small example in which there is enough time but the observations do not fit.
    """
    print("*** OBSERVATIONS DO NOT FIT ***")

    # Create the timeslots.
    # GN: 0 1 2 3  4  5
    # GS: 6 7 8 9 10 11
    timeslots = TimeSlots()

    # Create the list of observations. We will be working with the index of observation in this list.
    observations = Observations()

    # Observation 0
    observations.add_obs('1', [TS(0), TS(7), TS(10)], 600)

    # Observation 1
    observations.add_obs('2', [TS(3), TS(8)], 900)

    # Observation 2
    observations.add_obs('3', [TS(0), TS(1), TS(2), TS(3), TS(4),
                               TS(6), TS(7), TS(8), TS(9), TS(10)], 600)  # Unschedulable,

    # Observation 3
    observations.add_obs('1', [TS(0), TS(7), TS(10)], 600)

    # Observation 4
    observations.add_obs('2', [TS(0), TS(3), TS(4), TS(7), TS(9), TS(10), TS(11)], 300)

    # Observation 5
    observations.add_obs('2', [TS(0), TS(7), TS(10)], 600)

    observations.calculate_priority()
    print_observations(observations, timeslots)

    # Run the solver.
    print(f'\nScheduling {timeslots.num_timeslots_per_site * timeslots.timeslot_length} s per site...')
    final_schedule, final_score = schedule(timeslots, observations)
    print('Scheduling done.\n')

    print_schedule(timeslots, observations, final_schedule, final_score)


if __name__ == '__main__':
    # example_fully_scheduled(schedule)
    # example_underscheduled(schedule)
    # example_overscheduled(schedule)
    example_do_not_fit(schedule)
