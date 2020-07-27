# gurobi_solver.py
# By Sebastian Raaphorst, 2020.
# This gives a different, but still valid solution from lco_solver.

from __future__ import print_function
from math import ceil

from gurobipy import *

from common import *


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
    solver = Model('scheduler')

    # *** DECISION VARIABLES ***
    # Create the decision variables, Y_is: observation i can start in start slot s.
    y = []
    for obs_idx in range(observations.num_obs):
        yo = {ss_idx: solver.addVar(vtype=GRB.BINARY, name=('y_%d_%d' % (obs_idx, ss_idx)))
              for ss_idx in observations.start_slot_idx[obs_idx]}
        y.append(yo)
        solver.update()

    # *** CONSTRAINT TYPE 1 ***
    # First, no observation should be scheduled for more than one start.
    for obs_idx in range(observations.num_obs):
        expression = sum(y[obs_idx][k] for k in observations.start_slot_idx[obs_idx]) <= 1
        solver.addConstr(expression)

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
                if startslot_idx <= timeslot_idx < startslot_idx + \
                        ceil(int(observations.obs_time[obs_idx] / timeslots.timeslot_length)):
                    expression += y[obs_idx][startslot_idx]
        solver.addConstr(expression <= 1)

    observations.calculate_priority()

    # Create the objective function.
    objective_function = sum([observations.priority[obs_idx] * y[obs_idx][k]
                              for obs_idx in range(observations.num_obs)
                              for k in observations.start_slot_idx[obs_idx]])
    solver.setObjective(objective_function, GRB.MAXIMIZE)

    solver.update()
    solver.tune()
    solver.optimize()

    # Now get the score, which is the value of the objective function.
    # Right now, it is just a measure of the observations being scheduled (the score gets the priority of a
    # scheduled observation), but this will be much more complicated later on.
    schedule_score = solver.getObjective().getValue()

    # for idx1 in range(len(y)):
    #     for idx2 in y[idx1]:
    #         print(f'y[{idx1}][{idx2}] = {y[idx1][idx2]}')
    # print()

    final_schedule = [None] * (timeslots.num_timeslots_per_site * len(Resource))
    for timeslot_idx in range(timeslots.num_timeslots_per_site * len(Resource)):
        # Try to find a variable whose observation was scheduled for this timeslot.
        # Otherwise, the value for the timeslot will be None.
        for obs_idx in range(observations.num_obs):
            # Check to see if this timeslot is in the start slots for this observation, and if so,
            # if it was selected via the decision variable as the start slot for this observation.
            if timeslot_idx in y[obs_idx] and y[obs_idx][timeslot_idx].X == 1.0:
                # This is the start slot for the observation. Fill in the consecutive slots needed to complete it.
                # print(f'timeslot={timeslot_idx}, y[{obs_idx}][{timeslot_idx}]={y[obs_idx][timeslot_idx]}')
                for i in range(int(ceil(observations.obs_time[obs_idx] / timeslots.timeslot_length))):
                    final_schedule[timeslot_idx + i] = obs_idx
    return final_schedule, schedule_score
