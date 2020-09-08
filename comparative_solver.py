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
                         stop_time: int = DEFAULT_STOP_TIME) -> (TimeSlots, Observations):

    # 1 minute timeslots. We treat timeslots in minutes instead of seconds.
    timeslots = TimeSlots(num_timeslots_per_site=DEFAULT_NUM_TIMESLOTS_PER_SITE, timeslot_length=1)

    observations = Observations()

    for _ in range(num):
        band = str(randrange(1, 4))
        resource = Resource(randrange(3))

        obs_time = randrange(DEFAULT_OBS_TIME_LOWER, DEFAULT_OBS_TIME_UPPER)

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
            lb_time_constraint = DEFAULT_START_TIME
        if ub_time_constraint is None:
            ub_time_constraint = DEFAULT_STOP_TIME

        start_slots_gn = []
        start_slots_gs = []
        if resource == Resource.GN or resource == Resource.Both:
            start_slots_gn = [TS(i) for i in range(DEFAULT_NUM_TIMESLOTS_PER_SITE)
                              if lb_time_constraint <= i <= ub_time_constraint - obs_time]
        if resource == Resource.GS or resource == Resource.Both:
            start_slots_gs = [TS(i + DEFAULT_NUM_TIMESLOTS_PER_SITE) for i in range(DEFAULT_NUM_TIMESLOTS_PER_SITE)
                              if lb_time_constraint <= i <= ub_time_constraint - obs_time]
        start_slots = start_slots_gn + start_slots_gs

        observations.add_obs(band, resource, start_slots, obs_time, obs_time)

    observations.calculate_priority()
    return observations, timeslots


if __name__ == '__main__':
    seed(0)
    observations, timeslots = generate_random_data(DEFAULT_NUM_OBSERVATIONS)
    observations.calculate_priority()
    print_observations(observations, timeslots)

    # Run the solver.
    start_time = time.monotonic()
    final_schedule, final_score = schedule(timeslots, observations)
    end_time = time.monotonic()
    print_schedule(timeslots, observations, final_schedule, final_score)
    print(f"Time: {end_time - start_time} s")

