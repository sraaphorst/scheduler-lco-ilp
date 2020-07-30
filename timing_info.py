# timing_info.py
# By Sebastian Raaphorst, 2020.

# Alternate between LCO and Gurobi by switching the following imports:
# from lco_solver import *
from gurobi_solver import *

from random import seed, random, randrange, sample, uniform
import time


def generate_random_observation(observations: Observations,
                                timeslots: TimeSlots,
                                timeslot_alllowance_min: float = 0.01,
                                timeslot_allowance_max: float = 0.03):
    """
    Add a random observation to the collection of observations.
    :param observations: the collection of Observation objects
    :param timeslots: the collection of TimeSlot objects
    :param timeslot_alllowance_min: the min % of timeslots an observation can be fit in.
    :param timeslot_allowance_max: the max % of timeslots an observation can be fit in.
    """
    # Generate the band uniformly, from 1, 2, 3.
    band = str(randrange(1, 4))

    # Generate the length of the observation uniformly, from 30 minutes to three hours.
    # Represented in seconds, 6 is 30 minutes, 36 is three hours.
    # 300 seconds = 5 minutes.
    length = 300 * randrange(6, 36)

    # Now decide which timeslots we can insert into, and their metric.
    total_num_timeslots = timeslots.num_timeslots_per_site * 2
    num_timeslots = int(uniform(timeslot_alllowance_min, timeslot_allowance_max) * total_num_timeslots)
    timeslot_indices = sorted(sample(range(total_num_timeslots), num_timeslots))
    timeslots = [TS(idx, random()) for idx in timeslot_indices]

    observations.add_obs(band, timeslots, length)


if __name__ == '__main__':
    # Set the seed for consistent results.
    seed(0)

    # We want a month (30 days) of timeslots per site. Each timeslot is 5 minutes.
    # Assume 10 hours of darkness per day.
    num_days = 10
    num_timeslots_per_site = 5 * 12 * 10 * num_days
    timeslots = TimeSlots(num_timeslots_per_site=num_timeslots_per_site)

    print(f"Created {timeslots.num_timeslots_per_site} timeslots of length "
          f"{timeslots.timeslot_length} s each for each site...\n")

    # Create observations.
    num_observations = 100
    observations = Observations()
    for _ in range(num_observations):
        generate_random_observation(observations, timeslots)
    observations.calculate_priority()
    print(f"Created {num_observations} observations.")

    # Run the solver.
    start_time = time.monotonic()
    final_schedule, final_score = schedule(timeslots, observations)
    end_time = time.monotonic()
    print_schedule(timeslots, observations, final_schedule, final_score)
    print(f"Time: {end_time - start_time} s")


