from __future__ import print_function
from typing import List, Mapping, Tuple
from ortools.linear_solver import pywraplp

from input_parameters import *

# The schedule consists of a map between timeslot indices and
# observation indices - if any - to be run in those time slots.
Schedule = Mapping[int, int]

# The final score for this schedule, based on observation prorities.
Score = int


def schedule(timeslots: TimeSlots, observations: List[Observation]) -> Tuple[Schedule, Score]:
    """
    Given a set of timeslots and observations as defined in input_parameters,
    try to schedule as many observations as possible according to priority.
    The schedule is a mapping from timeslot indices to observation indices.

    Observations will
    :param timeslots: the timeslots as created by input_parameters.create_timeslots
    :param observations: the list of observations
    :return: a tuple of Schedule as defined above, and the score for the schedule 
    """

    # Enumerated observations: we want to work with the index of the observations.
    enumerated_observations = list(enumerate(observations))

    # Create the MIP solver.
    solver = pywraplp.Solver("scheduler",
                             pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    # *** DECISION VARIABLES ***
    # Create the decision variables, Y_ik.
    y = []
    for obs_idx, obs in enumerated_observations:
        yo = {k: solver.BoolVar('y_%d_%d' % (obs_idx, k)) for k in obs.start_slots}
        y.append(yo)

    # *** CONSTRAINT TYPE 1 ***
    # First, no observation should be scheduled for more than one start.
    for obs_idx, obs in enumerated_observations:
        expression = sum(y[obs_idx][k] for k in obs.start_slots) <= 1
        solver.Add(expression)

    # *** CONSTRAINT TYPE 2 ***
    # No more than one observation should be scheduled in each slot.
    for timeslot_idx, timeslot in list(enumerate(timeslots)):
        # This handles the case where if an observation starts in time slot t, it runs to completion,
        # occupying all the needed time slots.
        # The for comprehension is messy here, and requires repeated calculations, so we use loops.
        expression = 0
        for obs_idx, obs in enumerated_observations:
            # Calculate the number of slots needed for this observation.
            slots_needed = int(ceil(obs.observation_length / TIMESLOT_LENGTH))

            # For each possible start slot for this observation:
            for startslot_idx in obs.start_slots:
                # a_ikt * Y_ik -> a_ikt is 1 if starting obs obs_idx in startslot_idx means that it will occupy
                # slot timeslot, else 0.
                #
                # Thus, to simplify over LCO, instead of using a_ikt, we include Y_ik
                # in this constraint if starting at startslot means that the observation will occupy
                # timeslot (a_ikt = 1), and we omit it otherwise (a_ikt = 0)
                if startslot_idx <= timeslot_idx < startslot_idx + slots_needed:
                    expression += y[obs_idx][startslot_idx]
        solver.Add(expression <= 1)

    # Create the objective function.
    objective_function = sum([obs.priority * y[obs_idx][k]
                         for obs_idx, obs in enumerated_observations
                         for k in obs.start_slots])
    solver.Maximize(objective_function)

    # Run the solver.
    solver.Solve()

    # Now get the score.
    score = solver.Objective().Value()

    #for obs_idx, obs in enumerated_observations:
    #    for startslot_idx in obs.start_slots:
    #        print('y[%s][%s] = %s' % (obs_idx, startslot_idx, y[obs_idx][startslot_idx].solution_value()))

    # Iterate over each timeslot index and see if an observation has been scheduled for it.
    final_schedule = {}
    for timeslot_idx in range(NUM_TIMESLOTS_PER_SITE * 2):
        # Try to find a variable whose observation was scheduled for this timeslot.
        # Otherwise, the value for the timeslot will be None.
        for obs_idx, obs in enumerated_observations:
            # Check to see if this timeslot is in the start slots for this observation, and if so,
            # if it was selected via the decision variable as the start slot for this observation.
            if timeslot_idx in y[obs_idx] and y[obs_idx][timeslot_idx].solution_value() == 1:
                # This is the start slot for the observation. Fill in the consecutive slots needed to complete it.
                slots_needed = int(ceil(obs.observation_length / TIMESLOT_LENGTH))
                for i in range(slots_needed):
                    final_schedule[timeslot_idx + i] = obs_idx

    return final_schedule, score


if __name__ == '__main__':
    # GN: 0 1 2 3 4
    # GS: 5 6 7 8 9
    timeslots = create_timeslots()
    observations = [
        Observation(4, 600, [2, 5]),
        Observation(3, 900, [0, 1, 2, 7]),
        Observation(3, 1200, [0, 6]),
        Observation(4, 300, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    ]

    final_schedule, score = schedule(timeslots, observations)
    print("Score: %d" % score)
    print('Schedule:')
    for ts_idx in range(NUM_TIMESLOTS_PER_SITE * 2):
        site = ts_idx // NUM_TIMESLOTS_PER_SITE
        if ts_idx in final_schedule:
            print("%s %d: %d" % (Resource(site).name, ts_idx % NUM_TIMESLOTS_PER_SITE, final_schedule[ts_idx]))
        else:
            print("%s %d: None" % (Resource(site).name, ts_idx % NUM_TIMESLOTS_PER_SITE))
