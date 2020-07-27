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
    observations.add_obs('3', [0, 1, 2, 5, 6, 9], 300),
    observations.add_obs('2', [0, 3, 8], 900),
    observations.add_obs('3', [1, 3, 4, 8, 10], 600),
    observations.add_obs('1', [0, 3, 6, 9, 11], 300),
    observations.add_obs('2', [1, 3, 7, 9], 900),
    observations.add_obs('1', [3, 5, 6, 8, 10], 600)

    observations.calculate_priority()
    print_observations(observations, timeslots)

    # Run the solver.
    print(f'\nScheduling {timeslots.num_timeslots_per_site * timeslots.timeslot_length} s per site...')
    final_schedule, final_score = schedule(timeslots, observations)
    print('Scheduling done.\n')

    print_schedule(timeslots, final_schedule, final_score)


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
    observations.add_obs('2', [0, 7, 9], 800),
    observations.add_obs('1', [0, 2, 4], 600),
    observations.add_obs('1', [3], 900),
    observations.add_obs('3', [2, 5, 6, 10], 300),
    observations.add_obs('3', [1, 3, 5, 6, 10], 300),

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
    observations.add_obs('1', [0, 1, 3, 6, 7, 8, 9], 900),
    observations.add_obs('2', [1, 3, 7, 8], 900),
    observations.add_obs('2', [1, 2, 3, 4, 6, 8, 9, 10], 600),
    observations.add_obs('1', [0, 2, 6, 7, 8], 1200),
    observations.add_obs('3', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 300)
    observations.add_obs('3', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 300)

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
    observations.add_obs('1', [0, 7, 10], 600),
    observations.add_obs('2', [3, 9], 900),
    observations.add_obs('3', [0, 1, 2, 3, 4, 6, 7, 8, 9, 10], 600),  # Unschedulable,
    observations.add_obs('1', [0, 7, 10], 600),
    observations.add_obs('2', [0, 3, 4, 7, 9, 10, 11], 300)
    observations.add_obs('2', [0, 7, 10], 600)

    observations.calculate_priority()
    print_observations(observations, timeslots)

    # Run the solver.
    print(f'\nScheduling {timeslots.num_timeslots_per_site * timeslots.timeslot_length} s per site...')
    final_schedule, final_score = schedule(timeslots, observations)
    print('Scheduling done.\n')

    print_schedule(timeslots, observations, final_schedule, final_score)



if __name__ == '__main__':
    #print(timeit.timeit(stmt=run, number=10000))
    example4(schedule)
