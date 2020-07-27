# lco_examples.py
# By Sebastian Raaphorst, 2020.

from lco_solver import *


def run1():
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


if __name__ == '__main__':
    #print(timeit.timeit(stmt=run, number=10000))
    run1()