# timeslot_metric_example.py
# By Sebastian Raaphorst, 2020.

# Alternate between CBC and Gurobi by switching the following imports.
# Note that gurobi_solver coincidentally solves these the same, but could return any permutation as cbc_solver does.
from cbc_solver import *
# from gurobi_solver import *


def example_metric(schedule: Scheduler) -> None:
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

    # The variables are still Y_o,t for o an observation, t a timeslot with
    # value 1 if o is scheduled at t, and 0 otherwise.

    # The objective function was originally:
    # sum_{o in O} m(o) (sum_{t in T} Y_o,t)

    # The objective function becomes:
    # sum_{o in O} m(o) (sum_{t in T} m_o(t) Y_o,t)
    #                                 ^^^^^^
    # where m_o(t) is the metric function for observation o on the timeslots.

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


def example_nometric(schedule: Scheduler) -> None:
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
