# comparative_solver
# By Sebastian Raaphorst, 2020.
#
# Using the same observations as the genetic algorithm solver and a time unit of 1 minute, solve the same
# problem using solvers and determine the solution.

from defaults import *

# Alternate between CBC and Gurobi by switching the following imports:
# from cbc_solver import *
from gurobi_solver import *

from random import random, randrange, seed
import time


def generate_random_data(num: int,
                         start_time: int = DEFAULT_START_TIME,
                         stop_time: int = DEFAULT_STOP_TIME,
                         timeslot_length: int = DEFAULT_TIMESLOT_LENGTH) -> (TimeSlots, Observations):

    # Granular timeslots. We treat timeslots in minutes instead of seconds.
    num_timeslots_per_site = int((stop_time - start_time) / timeslot_length)
    timeslots = TimeSlots(timeslot_length, num_timeslots_per_site)
    observations = Observations()

    for _ in range(num):
        band = str(randrange(1, 4))
        resource = Resource(randrange(3))

        obs_time = randrange(obs_time_lower, obs_time_upper)

        lb_time_constraint = None
        ub_time_constraint = None
        while True:
            lb_time_constraint = randrange(start_time, stop_time) if random() < 0.2 else None
            ub_time_constraint = randrange(start_time, stop_time) if random() < 0.2 else None
            if lb_time_constraint is None or ub_time_constraint is None:
                break
            if lb_time_constraint < ub_time_constraint:
                break
        if lb_time_constraint is None:
            lb_time_constraint = start_time
        if ub_time_constraint is None:
            ub_time_constraint = stop_time
        start_slots_gn = []
        start_slots_gs = []
        if resource == Resource.GN or resource == Resource.Both:
            start_slots_gn = [TS(i) for i in range(num_timeslots_per_site)
                              if lb_time_constraint <= i * timeslot_length <= ub_time_constraint - obs_time]
        if resource == Resource.GS or resource == Resource.Both:
            start_slots_gs = [TS(i + num_timeslots_per_site) for i in range(num_timeslots_per_site)
                              if lb_time_constraint <= i * timeslot_length <= ub_time_constraint - obs_time]
        start_slots = start_slots_gn + start_slots_gs
        print(f"R: {resource}, len={obs_time}, lb={lb_time_constraint}, ub={ub_time_constraint}, upperb={ub_time_constraint - obs_time}, gn={start_slots_gn}, gs={start_slots_gs}")

        observations.add_obs(band, resource, start_slots, obs_time, obs_time)

    observations.calculate_priority()
    return observations, timeslots


if __name__ == '__main__':
    # stop_times = [600, 4200, 54000]
    # obs_time_lowers = [15, 30, 60]
    # obs_time_uppers = [60, 120, 240, 480]
    # num_obss = [100, 200, 500]
    # granularities = [1, 3, 5]
    stop_times = [60]
    obs_time_lowers = [5]
    obs_time_uppers = [20]
    num_obss = [10]
    granularities = [5]
    for stop_time in stop_times:
        for obs_time_lower in obs_time_lowers:
            for obs_time_upper in obs_time_uppers:
                for num_obs in num_obss:
                    for granularity in granularities:
                        #output = open(f'res-{stop_time}-{obs_time_lower}-{obs_time_upper}-{num_obs}-{granularity}.txt',
                        #              'w')
                        output = None
                        start_time = monotonic()
                        header = f"*** TIME={stop_time}, OBS_LB={obs_time_lower}, " +\
                                 f"OBS_UB={obs_time_upper} NUM_OBS={num_obs}, " +\
                                 f"GRANULARITY={granularity} ***"
                        print(header)
                        #output.write(header + '\n')

                        # Reset the RNG for consistent observations.
                        seed(0)
                        observations, timeslots = generate_random_data(num_obs, 0, stop_time, granularity)
                        observations.calculate_priority()
                        print_observations(observations, timeslots)

                        # Run the solver.
                        final_schedule, final_score = schedule(timeslots, observations, output)
                        print_schedule(timeslots, observations, final_schedule, final_score, output)
                        time_str = f"Time: {monotonic() - start_time} s\n"
                        print(time_str)
                        # output.write(time_str + '\n')
                        # output.close()

