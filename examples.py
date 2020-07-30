# examples.py
# By Sebastian Raaphorst, 2020.

# Alternate between LCO and Gurobi by switching the following imports:
#from lco_solver import *
from gurobi_solver import *


def example1(schedule):
    """
    A small example which will schedule fully all observations.
    """
    # Create the timeslots.
    # GN: 0 1 2 3  4  5
    # GS: 6 7 8 9 10 11
    timeslots = TimeSlots()

    # Create the list of observations. We will be working with the index of observation in this list.
    observations = Observations()
    observations.add_obs('3', [TS(0), TS(1), TS(2), TS(5), TS(6), TS(9)], 300),
    observations.add_obs('2', [TS(0), TS(3), TS(8)], 900),
    observations.add_obs('3', [TS(1), TS(3), TS(4), TS(8), TS(10)], 600),
    observations.add_obs('1', [TS(0), TS(3), TS(6), TS(9), TS(11)], 300),
    observations.add_obs('2', [TS(1), TS(3), TS(7), TS(9)], 900),
    observations.add_obs('1', [TS(3), TS(5), TS(6), TS(8), TS(10)], 600)

    observations.calculate_priority()
    print_observations(observations, timeslots)

    # Run the solver.
    print(f'\nScheduling {timeslots.num_timeslots_per_site * timeslots.timeslot_length} s per site...')
    final_schedule, final_score = schedule(timeslots, observations)
    print('Scheduling done.\n')

    print_schedule(timeslots, observations, final_schedule, final_score)


def example2(schedule):
    """
    A small example which will schedule fully all observations and have room left over.
    One of the observations has slack time of 100 s, i.e. observation 1.
    """
    # Create the timeslots.
    # GN: 0 1 2 3  4  5
    # GS: 6 7 8 9 10 11
    timeslots = TimeSlots()

    # Create the list of observations. We will be working with the index of observation in this list.
    observations = Observations()
    observations.add_obs('2', [TS(0), TS(7), TS(9)], 800),
    observations.add_obs('1', [TS(0), TS(2), TS(4)], 600),
    observations.add_obs('1', [TS(3)], 900),
    observations.add_obs('3', [TS(2), TS(5), TS(6), TS(10)], 300),
    observations.add_obs('3', [TS(1), TS(3), TS(5), TS(6), TS(10)], 300),

    observations.calculate_priority()
    print_observations(observations, timeslots)

    # Run the solver.
    print(f'\nScheduling {timeslots.num_timeslots_per_site * timeslots.timeslot_length} s per site...')
    final_schedule, final_score = schedule(timeslots, observations)
    print('Scheduling done.\n')

    print_schedule(timeslots, observations, final_schedule, final_score)


def example3(schedule):
    """
    A small example which will cannot fully schedule all observations as there is insufficient time.
    """
    # Create the timeslots.
    # GN: 0 1 2 3  4  5
    # GS: 6 7 8 9 10 11
    timeslots = TimeSlots()

    # Create the list of observations. We will be working with the index of observation in this list.
    observations = Observations()
    observations.add_obs('1', [TS(0), TS(1), TS(3), TS(6), TS(7), TS(8), TS(9)], 900),
    observations.add_obs('2', [TS(1), TS(3), TS(7), TS(8)], 900),
    observations.add_obs('2', [TS(1), TS(2), TS(3), TS(4), TS(6), TS(8), TS(9), TS(10)], 600),
    observations.add_obs('1', [TS(0), TS(2), TS(6), TS(7), TS(8)], 1200),
    observations.add_obs('3', [TS(0), TS(1), TS(2), TS(3), TS(4), TS(5),
                               TS(6), TS(7), TS(8), TS(9), TS(10), TS(11)], 300)
    observations.add_obs('3', [TS(0), TS(1), TS(2), TS(3), TS(4), TS(5),
                               TS(6), TS(7), TS(8), TS(9), TS(10), TS(11)], 300)

    observations.calculate_priority()
    print_observations(observations, timeslots)

    # Run the solver.
    print(f'\nScheduling {timeslots.num_timeslots_per_site * timeslots.timeslot_length} s per site...')
    final_schedule, final_score = schedule(timeslots, observations)
    print('Scheduling done.\n')

    print_schedule(timeslots, observations, final_schedule, final_score)


def example4(schedule):
    """
    A small example in which there is enough time but the observations do not fit.
    """
    # Create the timeslots.
    # GN: 0 1 2 3  4  5
    # GS: 6 7 8 9 10 11
    timeslots = TimeSlots()

    # Create the list of observations. We will be working with the index of observation in this list.
    observations = Observations()
    observations.add_obs('1', [TS(0), TS(7), TS(10)], 600),
    observations.add_obs('2', [TS(3), TS(9)], 900),
    observations.add_obs('3', [TS(0), TS(1), TS(2), TS(3), TS(4),
                               TS(6), TS(7), TS(8), TS(9), TS(10)], 600),  # Unschedulable,
    observations.add_obs('1', [TS(0), TS(7), TS(10)], 600),
    observations.add_obs('2', [TS(0), TS(3), TS(4), TS(7), TS(9), TS(10), TS(11)], 300)
    observations.add_obs('2', [TS(0), TS(7), TS(10)], 600)

    observations.calculate_priority()
    print_observations(observations, timeslots)

    # Run the solver.
    print(f'\nScheduling {timeslots.num_timeslots_per_site * timeslots.timeslot_length} s per site...')
    final_schedule, final_score = schedule(timeslots, observations)
    print('Scheduling done.\n')

    print_schedule(timeslots, observations, final_schedule, final_score)


def example5(schedule):
    """
    Small example to show the timeslot priority per observation.
    """
    # Create the timeslots.
    # GN: 0 1 2 3  4  5
    # GS: 6 7 8 9 10 11
    timeslots = TimeSlots()

    # Create the list of observations. We will be working with the index of observation in this list.
    observations = Observations()
    observations.add_obs('3', [TS(0, 0.25), TS(2, 0.5), TS(4, 1),
                               TS(6, 0.125), TS(8, 0.125), TS(10, 0.125)], 600)  # 0
    observations.add_obs('2', [TS(0, 0.5), TS(2, 1), TS(4, 0.5),
                               TS(6, 0.125), TS(8, 0.125), TS(10, 0.125)], 600)  # 1
    observations.add_obs('1', [TS(0, 1), TS(2, 0.5), TS(4, 0.25),
                               TS(6, 0.125), TS(8, 0.125), TS(10, 0.125)], 600)  # 2
    observations.add_obs('2', [TS(0, 0.25), TS(3, 0.25),
                               TS(6, 0.5), TS(9, 1)], 900)  # 3
    observations.add_obs('1', [TS(0, 0.25), TS(3, 0.25),
                               TS(6, 1), TS(9, 0.5)], 900)  # 4

    observations.calculate_priority()
    print_observations(observations, timeslots)

    # Run the solver.
    print(f'\nScheduling {timeslots.num_timeslots_per_site * timeslots.timeslot_length} s per site...')
    final_schedule, final_score = schedule(timeslots, observations)
    print('Scheduling done.\n')

    print_schedule(timeslots, observations, final_schedule, final_score)


def example6(schedule):
    """
    Same as example 5 but without timeslot metric so any permutation can occur.
    """
    # Create the timeslots.
    # GN: 0 1 2 3  4  5
    # GS: 6 7 8 9 10 11
    timeslots = TimeSlots()

    # Create the list of observations. We will be working with the index of observation in this list.
    observations = Observations()
    observations.add_obs('1', [TS(0), TS(2), TS(4), TS(6), TS(8), TS(10)], 600)
    observations.add_obs('2', [TS(0), TS(2), TS(4), TS(6), TS(8), TS(10)], 600)
    observations.add_obs('3', [TS(0), TS(2), TS(4), TS(6), TS(8), TS(10)], 600)
    observations.add_obs('1', [TS(0), TS(3), TS(6), TS(9)], 900)
    observations.add_obs('2', [TS(0), TS(3), TS(6), TS(9)], 900)

    observations.calculate_priority()
    print_observations(observations, timeslots)

    # Run the solver.
    print(f'\nScheduling {timeslots.num_timeslots_per_site * timeslots.timeslot_length} s per site...')
    final_schedule, final_score = schedule(timeslots, observations)
    print('Scheduling done.\n')

    print_schedule(timeslots, observations, final_schedule, final_score)


if __name__ == '__main__':
    #print(timeit.timeit(stmt=run, number=10000))
    #example1(schedule)
    #example2(schedule)
    #example3(schedule)
    #example4(schedule)

    print('*** WITH METRIC ON TIMESLOTS ***')
    example5(schedule)
    print('\n\n*** WITH NO METRIC ON TIMESLOTS ***')
    example6(schedule)
