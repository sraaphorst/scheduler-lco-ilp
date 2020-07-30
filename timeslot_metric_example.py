# timeslot_metric_example.py
# By Sebastian Raaphorst, 2020.

# Alternate between LCO and Gurobi by switching the following imports.
# Note that Gurobi coincidentally solves these the same, but could return any permutation as lco_scheduler does.
from lco_solver import *
#  from gurobipy import *


def example_metric(schedule):
    """
    Small example to show the timeslot priority per observation.
    """
    # Create the timeslots.
    # GN: 0 1 2 3  4  5
    # GS: 6 7 8 9 10 11
    timeslots = TimeSlots()

    # Create the list of observations. We will be working with the index of observation in this list.
    observations = Observations()
    # observations.add_obs('3', [TS(0, 0.25), TS(2, 0.5), TS(4, 1),
    #                            TS(6, 0.125), TS(8, 0.125), TS(10, 0.125)], 600)  # 0
    # observations.add_obs('2', [TS(0, 0.5), TS(2, 1), TS(4, 0.5),
    #                            TS(6, 0.125), TS(8, 0.125), TS(10, 0.125)], 600)  # 1
    # observations.add_obs('1', [TS(0, 1), TS(2, 0.5), TS(4, 0.25),
    #                            TS(6, 0.125), TS(8, 0.125), TS(10, 0.125)], 600)  # 2
    # observations.add_obs('2', [TS(0, 0.25), TS(3, 0.25),
    #                            TS(6, 0.5), TS(9, 1)], 900)  # 3
    # observations.add_obs('1', [TS(0, 0.25), TS(3, 0.25),
    #                            TS(6, 1), TS(9, 0.5)], 900)  # 4

    # Metric curve for observation 1 is based on:
    # y = max(0.1, -(1/10)(x - 2)^2 + 1)
    # and shifted around for different observations.

    # Observation 0
    observations.add_obs('3', [TS(0, 1), TS(1, 0.9), TS(2, 0.6), TS(3, 0.1), TS(4, 0.1),
                               TS(6, 0.1), TS(7, 0.1), TS(8, 0.1), TS(9, 0.1), TS(10, 0.1)], 600)

    # Observation 1
    observations.add_obs('1', [TS(0, 0.6), TS(1, 0.9), TS(2, 1), TS(3, 0.9), TS(4, 0.6),
                               TS(6, 0.1), TS(7, 0.1), TS(8, 0.1), TS(9, 0.1), TS(10, 0.1)], 600)

    # Observation 2
    observations.add_obs('2', [TS(0, 0.1), TS(1, 0.1), TS(2, 0.6), TS(3, 0.9), TS(4, 1),
                               TS(6, 0.1), TS(7, 0.1), TS(8, 0.1), TS(9, 0.1), TS(10, 0.1)], 600)

    # Observation 3
    observations.add_obs('1', [TS(0, 0.1), TS(1, 0.1), TS(2, 0.1), TS(3, 0.1), TS(4, 0.1),
                               TS(6, 1), TS(7, 0.9), TS(8, 0.6), TS(9, 0.1)], 900)

    # Observation 4
    observations.add_obs('2', [TS(0, 0.1), TS(1, 0.1), TS(2, 0.1), TS(3, 0.1), TS(4, 0.1),
                               TS(6, 0.1), TS(7, 0.6), TS(8, 0.9), TS(9, 1)], 900)

    observations.calculate_priority()
    print_observations(observations, timeslots)

    # Run the solver.
    print(f'\nScheduling {timeslots.num_timeslots_per_site * timeslots.timeslot_length} s per site...')
    final_schedule, final_score = schedule(timeslots, observations)
    print('Scheduling done.\n')

    print_schedule(timeslots, observations, final_schedule, final_score)


def example_nometric(schedule):
    """
    Same as example_metric but without timeslot metric so any permutation can occur.
    """
    # Create the timeslots.
    # GN: 0 1 2 3  4  5
    # GS: 6 7 8 9 10 11
    timeslots = TimeSlots()

    # Create the list of observations. We will be working with the index of observation in this list.
    observations = Observations()

    # Observation 0
    observations.add_obs('3', [TS(0), TS(1), TS(2), TS(3), TS(4),
                               TS(6), TS(7), TS(8), TS(9), TS(10)], 600)

    # Observation 1
    observations.add_obs('1', [TS(0), TS(1), TS(2), TS(3), TS(4),
                               TS(6), TS(7), TS(8), TS(9), TS(10)], 600)

    # Observation 2
    observations.add_obs('2', [TS(0), TS(1), TS(2), TS(3), TS(4),
                               TS(6), TS(7), TS(8), TS(9), TS(10)], 600)

    # Observation 3
    observations.add_obs('1', [TS(0), TS(1), TS(2), TS(3),
                               TS(6), TS(7), TS(8), TS(9)], 900)

    # Observation 4
    observations.add_obs('2', [TS(0), TS(1), TS(2), TS(3),
                               TS(6), TS(7), TS(8), TS(9)], 900)

    observations.calculate_priority()
    print_observations(observations, timeslots)

    # Run the solver.
    print(f'\nScheduling {timeslots.num_timeslots_per_site * timeslots.timeslot_length} s per site...')
    final_schedule, final_score = schedule(timeslots, observations)
    print('Scheduling done.\n')

    print_schedule(timeslots, observations, final_schedule, final_score)


if __name__ == '__main__':
    print('*** WITH METRIC ON TIMESLOTS ***')
    example_metric(schedule)
    print('\n\n*** WITH NO METRIC ON TIMESLOTS ***')
    example_nometric(schedule)