# comparative_solver
# By Sebastian Raaphorst, 2020.
#
# Using the same observations as the genetic algorithm solver and a time unit of 1 minute, solve the same
# problem using solvers and determine the solution.

from astropy.table import Table
from astropy.time import Time

from defaults import *

# Alternate between CBC and Gurobi by switching the following imports:
from cbc_solver import *
# from gurobi_solver import *

from random import random, randrange, seed


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

        observations.add_obs(band, resource, start_slots, obs_time, obs_time)

    observations.calculate_priority()
    return observations, timeslots


if __name__ == '__main__':
    stop_times = [173 * 3]
    obs_times = [(45, 60), (10, 180)]
    num_obss = [1200]
    granularities = [3]

    # stop_times = [60]
    # obs_time_lowers = [5]
    # obs_time_uppers = [20]
    # num_obss = [10]
    # granularities = [3]

    obstab = Table.read('obstab.fits')
    targtab_metvis = Table.read('targtab_metvis.fits')
    targtab_metvisha = Table.read('targtab_metvisha.fits')

    # Get the obs_id of the observations we are considering.
    obs_ids = [row['obs_id'] for row in obstab]
    #print(f"observations: {obs_ids}")

    # Get the fixed priorities for the observations. These are 0 or a fixed constant.
    # If they are 0, do not include them. If they are a fixed constant, include them.
    priority_list = {obs_id: enumerate(row['weight']) for obs_id in obs_ids for row in targtab_metvis
                     if row['id'] == obs_id}
    start_slots = {obs_id : [id for id, prio in priority_list[obs_id] if prio > 0] for obs_id in obs_ids}

    # Get the remaining observation lengths.
    obs_lengths = {row['obs_id']: (row['tot_time'] - row['obs_time']) * 60 for row in obstab}

    # Drop the last start slots that aren't feasible to start in, as they would be starting too late to complete.
    adjusted_start_slots = {}
    for obs_id in start_slots:
        start_slot_list = start_slots[obs_id]
        print(f"{obs_id} -> {start_slot_list}")
        adjusted_list_len = max(0, len(start_slot_list) - int(ceil(obs_lengths[obs_id] / 3)))
        start_slot_list = start_slot_list[:adjusted_list_len]
        adjusted_start_slots[obs_id] = start_slot_list
    start_slots = adjusted_start_slots
    #start_slots = {obs_id : start_slots[:(len(start_slots)-int(ceil(obs_lengths[obs_id] / 3)))] for obs_id in obs_ids}

    priorities = {}
    for obs_id, row in zip(obs_ids, targtab_metvis):
        assert(obs_id == row['id'])
        priorities[obs_id] = max(row['weight'])

    #print('*** START SLOTS ***')
    #print(start_slots)
    #print("\n\n\n*** PRIORITIES ***")
    #print(priorities)

    # Get the timeslot priorities for the observations.
    timeslot_priorities = {obs_id: row['weight'] for obs_id in obs_ids for row in targtab_metvisha
                           if row['id'] == obs_id}
    #print(timeslot_priorities)

    #print(obs_lengths)

    # Creat the timeslots: there should be 173, each of 3 minutes.
    timeslots = TimeSlots(3, 173)

    # Create the observations.
    obs = Observations()

    for obs_id in obs_ids:
        if priorities[obs_id] > 0:
            obs.add_obs(obs_id, Resource.GS, [TS(idx + timeslots.num_timeslots_per_site,
                                                 timeslot_priorities[obs_id][idx])
                                              for idx in start_slots[obs_id]], obs_lengths[obs_id], priorities[obs_id])

    print(obs.num_obs)
    print_observations(obs, timeslots)

    # Run the solver.
    final_schedule, final_score = schedule(timeslots, obs)
    print_schedule(timeslots, obs, final_schedule, final_score)


    # for stop_time in stop_times:
    #     for obs_time_lower, obs_time_upper in obs_times:
    #         for num_obs in num_obss:
    #             for granularity in granularities:
    #                 output = open(f'res-{stop_time}-{obs_time_lower}-{obs_time_upper}-{num_obs}-{granularity}.txt',
    #                                 'w')
    #                 start_time = monotonic()
    #                 header = f"*** TIME={stop_time}, OBS_LB={obs_time_lower}, " +\
    #                          f"OBS_UB={obs_time_upper} NUM_OBS={num_obs}, " +\
    #                          f"GRANULARITY={granularity} ***"
    #                 print(header)
    #                 output.write(header + '\n')
    #
    #                 # Reset the RNG for consistent observations.
    #                 seed(0)
    #                 observations, timeslots = generate_random_data(num_obs, 0, stop_time, granularity)
    #                 observations.calculate_priority()
    #                 #print_observations(observations, timeslots)
    #
    #                 # Run the solver.
    #                 final_schedule, final_score = schedule(timeslots, observations, output)
    #                 print_schedule(timeslots, observations, final_schedule, final_score, output)
    #                 time_str = f"Time: {monotonic() - start_time} s\n"
    #                 print(time_str)
    #                 output.write(time_str + '\n')
    #                 output.close()