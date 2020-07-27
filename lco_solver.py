# lco_solver.py
# By Sebastian Raaphorst, 2020.

from __future__ import print_function
from typing import List, Mapping, Tuple
from math import ceil

from ortools.linear_solver import pywraplp

from input_parameters import *
import timeit

# The schedule consists of a map between timeslot indices and
# observation indices - if any - to be run in those time slots.
Schedule = Mapping[int, int]

# The final score for this schedule, based on observation prorities.
Score = int


def schedule(timeslots: TimeSlots, observations: Observations) -> Tuple[Schedule, Score]:
    """
    Given a set of timeslots and observations as defined in input_parameters,
    try to schedule as many observations as possible according to priority.
    The schedule is a mapping from timeslot indices to observation indices.

    Observations will
    :param timeslots: the timeslots as created by input_parameters.create_timeslots
    :param observations: the Observations object containing the list of observations
    :return: a tuple of Schedule as defined above, and the score for the schedule 
    """

    # Note: Start slots run from 0 to 2 * NUM_SLOTS_PER_RESOURCE - 1, where each grouping of
    # i * NUM_SLOTS_PER_RESOURCE to (i+1) * NUM_SLOTS_PER_RESOURCE - 1 represents the slots
    # for resource i.

    # Enumerated timeslots: we want to work with the index of these objects.
    enumerated_timeslots = list(enumerate(timeslots))

    # Create the MIP solver.
    solver = pywraplp.Solver('scheduler', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    # *** DECISION VARIABLES ***
    # Create the decision variables, Y_is: observation i can start in start slot s.
    y = []
    for obs_idx in range(observations.num_obs):
        yo = {ss_idx: solver.BoolVar('y_%d_%d' % (obs_idx, ss_idx))
              for ss_idx in observations.start_slot_idx[obs_idx]}
        y.append(yo)

    # *** CONSTRAINT TYPE 1 ***
    # First, no observation should be scheduled for more than one start.
    for obs_idx in range(observations.num_obs):
        expression = sum(y[obs_idx][k] for k in observations.start_slot_idx[obs_idx]) <= 1
        solver.Add(expression)

    # *** CONSTRAINT TYPE 2 ***
    # No more than one observation should be scheduled in each slot.
    for timeslot_idx, timeslot in enumerated_timeslots:
        # This handles the case where if an observation starts in time slot t, it runs to completion,
        # occupying all the needed time slots.
        # The for comprehension is messy here, and requires repeated calculations, so we use loops.
        expression = 0
        for obs_idx in range(observations.num_obs):
            # For each possible start slot for this observation:
            for startslot_idx in observations.start_slot_idx[obs_idx]:
                # a_ikt * Y_ik -> a_ikt is 1 if starting obs obs_idx in startslot_idx means that it will occupy
                # slot timeslot, else 0.
                #
                # Thus, to simplify over LCO, instead of using a_ikt, we include Y_ik
                # in this constraint if starting at startslot means that the observation will occupy
                # timeslot (a_ikt = 1), and we omit it otherwise (a_ikt = 0)
                if startslot_idx <= timeslot_idx < startslot_idx +\
                        ceil(int(observations.obs_time[obs_idx] / timeslots.timeslot_length)):
                    expression += y[obs_idx][startslot_idx]
        solver.Add(expression <= 1)

    observations.calculate_priority()
    # Create the objective function.
    objective_function = sum([observations.priority[obs_idx] * y[obs_idx][k]
                              for obs_idx in range(observations.num_obs)
                              for k in observations.start_slot_idx[obs_idx]])
    solver.Maximize(objective_function)

    # Run the solver.
    solver.Solve()

    # Now get the score, which is the value of the objective function.
    # Right now, it is just a measure of the observations being scheduled (the score gets the priority of a
    # scheduled observation), but this will be much more complicated later on.
    schedule_score = solver.Objective().Value()

    for idx1 in range(len(y)):
        for idx2 in y[idx1]:
            print('y[%d][%d] = %s' % (idx1, idx2, y[idx1][idx2].solution_value()))
    print()

    # Iterate over each timeslot index and see if an observation has been scheduled for it.
    final_schedule = {}
    for timeslot_idx in range(timeslots.num_timeslots_per_site * len(Resource)):
        # Try to find a variable whose observation was scheduled for this timeslot.
        # Otherwise, the value for the timeslot will be None.
        for obs_idx in range(observations.num_obs):
            # Check to see if this timeslot is in the start slots for this observation, and if so,
            # if it was selected via the decision variable as the start slot for this observation.
            if timeslot_idx in y[obs_idx] and y[obs_idx][timeslot_idx].solution_value() == 1:
                print("timeslot=%s, y[%s][%s]=%s" % (timeslot_idx, obs_idx, timeslot_idx, y[obs_idx][timeslot_idx]))
                # This is the start slot for the observation. Fill in the consecutive slots needed to complete it.
                for i in range(int(ceil(observations.obs_time[obs_idx] / timeslots.timeslot_length))):
                    final_schedule[timeslot_idx + i] = obs_idx

    return final_schedule, schedule_score


def print_schedule(timeslots: TimeSlots, final_schedule: Schedule, final_score: Score):
    """
    Given the execution of a call to schedule, print the results.
    :param timeslots: the TimeSlots object
    :param final_schedule: the final schedule returned from schedule
    :param final_score: the final score returned from schedule
    """
    for site in Resource:
        print('Schedule for %s:' % site.name)
        print('\tTSIdx    ObsIdx')
        for ts_offset in range(timeslots.num_timeslots_per_site):
            ts_idx = ts_offset + site.value * timeslots.num_timeslots_per_site
            if ts_offset in final_schedule:
                print('\t    %d         %d' % (ts_offset, final_schedule[ts_idx]))
            else:
                print('\t    %d       None' % ts_offset)
        print()

    print('Score: %d\n' % final_score)


def run1():
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
