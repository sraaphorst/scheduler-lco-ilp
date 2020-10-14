# common.py
# By Sebastian Raaphorst, 2020.
# This file defines the objects that manage time slots and observations, and
# the primary output formatting.

from enum import IntEnum
from typing import List, Union, Tuple
from dataclasses import dataclass

import numpy as np


# The schedule consists of a map between timeslot indices and
# observation indices - if any - to be run in those time slots.
Schedule = List[Union[int, None]]


# The final score for this schedule, based on observation prorities.
Score = float


class Resource(IntEnum):
    """
    The resources (telescopes) to be scheduled.
    """
    GN = 0
    GS = 1
    Both = 2


# An alias for priority. Right now we use a simple int as a priority.
Priority = int


class TimeSlot:
    """
    A single representation of a time slot, which is a resource and a period of time.
    """
    def __init__(self, resource: Resource, start_time: int):
        """
        The definition of a time slot available for a resource.
        Note that time slots should NOT overlap, i.e. for a resource, e.g. GN, if we have a time slot
        TimeSlot(GN, 0), a TimeSlot(GN, 200) would be illegal as the times intersect.
        The timeslot begins at start_time and lasts for TIMESLOT_LENGTH.

        :param resource: the resource in question
        :param start_time: the start time of the time slot as an offset from 0, the initial start time
        """
        self.resource = resource
        self.start_time = start_time


class TimeSlots:
    """
    A collection of TimeSlot objects.
    """
    def __init__(self, timeslot_length: int = 5, num_timeslots_per_site: int = 6):
        """
        Create the collection of timeslots, which consist of a collection of TimeSlot
        objects as below for scheduling.

        For each resource, we begin at time 0 and create a timeslot.
        We then increment by TIMESLOT_LENGTH and create another timeslot.
        We continue to create timeslots until we have the specified number for each resource.

        :param timeslot_length: the length of the timeslots in s, default is 5 min
        :param num_timeslots_per_site: the number of timeslots per site
        """
        self.timeslot_length = timeslot_length
        self.num_timeslots_per_site = num_timeslots_per_site

        self.timeslots = []
        for r in Resource:
            if r == Resource.Both:
                continue
            for idx in range(num_timeslots_per_site):
                self.timeslots.append(TimeSlot(r, idx * timeslot_length))

    def get_timeslot(self, resource: Resource, index: int) -> TimeSlot:
        """
        Given a resource and an index into its timeslots, return the corresponding timeslot.
        :param resource: the Resource
        :param index: the index, in [0, NUM_TIMESLOTS_PER_SITE]
        :return: the TimeSlot, if it exists
        :except: ValueError if the index condition is violated
        """
        return self.timeslots[resource * self.num_timeslots_per_site + index]

    def __iter__(self):
        """
        Create an iterator for the time slots.
        :return: an iterator
        """
        return TimeSlotsIterator(self)


class TimeSlotsIterator:
    """
    Iterator class for TimeSlots.
    """
    def __init__(self, timeslots: TimeSlots):
        self._timeslots = timeslots
        self._index = 0

    def __next__(self) -> TimeSlot:
        """
        Returns the next time slot.
        :return: the next time slot
        :except: StopIteration when the iteration is done
        """
        if self._index < len(self._timeslots.timeslots):
            slot = self._timeslots.timeslots[self._index]
            self._index += 1
            return slot
        raise StopIteration


@dataclass
class TS:
    """
    This is just a dataclass to wrap a timeslot index and a metric score for
    that timeslot index together. It is a temporary measure to provide a metric
    for timeslots for each observation, which would otherwise be based on an
    actual metric function.

    This is factored into the objective function for each observation, so the
    objective function has an overall metric on observations, and then a metric
    (currently faux) function on timeslots per observation.

    :param timeslot_idx: the index of the timeslot
    :param metric_score: the metric score of the timeslot for the observation
    :return: a tuple representing
    """
    timeslot_idx: int
    metric_score: float = 1.0


class Observations:
    """
    The set of observations and the necessary information to formulate the mathematical ILP model
    to represent this as a scheduling problem.

    We schedule an observation every five minutes across a time range, during which an observation is valid at
    a certain resource or not.
    """

    def __init__(self):
        """
        Initialize to an empty set of observations.
        Right now, this is a mix of numpy and python as I think we need constructs from both.

        num_obs - the number of observations
        obs_time - the length of the observation
        start_slot_idxs - a list of timeslot indices representing what timeslots the observation can
                        can be observed at and their score for each time slot
        priority - the priority for each time slot (either 0 or a constant)
        """
        self.num_obs = 0
        self.name = np.empty((0,), dtype=str)
        self.resource = np.empty((0,), dtype=Resource)
        self.obs_time = np.empty((0,), dtype=float)
        self.start_slots = []
        self.priority = np.empty((0,), dtype=float)

    def add_obs(self, name: str, resource: Resource, start_slot_idx: List[TS], obs_time: float, priority: float) -> None:
        """
        Add an observation to the collection of observations.
        """
        self.name = np.append(self.name, name)
        self.resource = np.append(self.resource, resource)
        self.start_slots.append(start_slot_idx)
        self.obs_time = np.append(self.obs_time, obs_time)
        self.num_obs += 1
        self.priority = np.append(self.priority, priority)


GA_Schedule = List[Tuple[int, int]]


def schedule_transform(final_schedule: Schedule, observations: Observations, resource: Resource, timeslots: TimeSlots) -> GA_Schedule:
    """
    Convert to the same format used by the genetic algorithm, for output purposes.
    :param final_schedule: the schedule returned by the ILP solver
    :param timeslots: the timeslots
    :return: the GA scheduler equivalent
    """
    # Convert to same format as genetic algorithm: (start time, obs_idx).
    curr_time = 0
    sched = []
    for ts_idx, obs_idx in \
            enumerate(final_schedule[:timeslots.num_timeslots_per_site] if resource == Resource.GN
                      else final_schedule[timeslots.num_timeslots_per_site:]):
        if obs_idx is None or observations.resource[obs_idx] not in [resource, Resource.Both]:
            continue
        if len(sched) == 0 or sched[-1][1] != obs_idx:
            sched.append((ts_idx, obs_idx))
    return sched


def detailed_schedule(name: str, schedule: GA_Schedule, timeSlots: TimeSlots, observations: Observations,
                      stop_time: int) -> str:
    line_start = '\n\t' if name is not None else '\n'
    data = name if name is not None else ''

    obs_prev_time = 0
    for obs_start_time_slot, obs_idx in schedule:
        obs_start_time = obs_start_time_slot * timeSlots.timeslot_length
        gap_size = int(obs_start_time - obs_prev_time)
        if gap_size > 0e-3:
            data += line_start + f'Gap of  {gap_size:>3} min{"s" if gap_size > 1 else ""}'
        data += line_start + f'At time {obs_start_time:>3}: Observation {observations.name[obs_idx]:<15}, ' \
                             f'resource={Resource(observations.resource[obs_idx]).name:<4}, ' \
                             f'obs_time={int(observations.obs_time[obs_idx]):>3}, ' \
                             f'priority={observations.priority[obs_idx]:>4}'
        obs_prev_time = obs_start_time + observations.obs_time[obs_idx]

    gap_size = int(stop_time - obs_prev_time)
    if gap_size > 0e-3:
        data += line_start + f'Gap of  {gap_size:>3} min{"s" if gap_size > 1 else ""}'

    return data


def print_schedule(timeslots: TimeSlots, observations: Observations,
                   final_schedule: Schedule, final_score: Score, out = None) -> None:
    """
    Given the execution of a call to schedule, print the results.
    :param timeslots: the TimeSlots object
    :param observations: the Observations object
    :param final_schedule: the final schedule returned from schedule
    :param final_score: the final score returned from schedule
    """

    gn_sched = schedule_transform(final_schedule, observations, Resource.GN, timeslots)
    gs_sched = schedule_transform(final_schedule, observations, Resource.GS, timeslots)

    overall_score = f"Final score: {final_score}"
    if out is None:
        print(overall_score)
    else:
        out.write(overall_score + '\n')

    ### GN ###
    printable_schedule_gn = detailed_schedule("Gemini North:", gn_sched, timeslots, observations,
                                              timeslots.num_timeslots_per_site * timeslots.timeslot_length)
    if out is None:
        print(printable_schedule_gn)
    else:
        out.write(printable_schedule_gn + '\n')

    gn_obs = set([obs_idx for obs_idx in final_schedule[:timeslots.num_timeslots_per_site] if obs_idx is not None])
    gn_usage = sum(observations.obs_time[obs_idx] for obs_idx in gn_obs)
    gn_pct = gn_usage / (timeslots.num_timeslots_per_site * timeslots.timeslot_length) * 100
    gn_score = sum([observations.priority[obs_idx] for obs_idx in gn_obs])
    gn_summary = f'\tUsage: {gn_usage}, {gn_pct}%, Fitness: {gn_score}'
    if out is None:
        print(gn_summary + '\n')
    else:
        out.write(gn_summary + ('\n' * 2))

    # *** GS ***
    printable_schedule_gs = detailed_schedule("Gemini South:", gs_sched, timeslots, observations,
                                              timeslots.num_timeslots_per_site * timeslots.timeslot_length)
    if out is None:
        print(printable_schedule_gs)
    else:
        out.write(printable_schedule_gs + '\n')

    gs_obs = set([obs_idx for obs_idx in final_schedule[timeslots.num_timeslots_per_site:] if obs_idx is not None])
    gs_usage = sum(observations.obs_time[obs_idx] for obs_idx in gs_obs)
    gs_pct = gs_usage / (timeslots.num_timeslots_per_site * timeslots.timeslot_length) * 100
    #gs_score = sum([observations.priority[obs_idx] for obs_idx in gs_obs])
    gs_score = sum([observations.priority[obs_idx] * observations.obs_time[obs_idx] for obs_idx in gs_obs]) / (timeslots.num_timeslots_per_site * timeslots.timeslot_length)
    gs_summary = f'\tUsage: {gs_usage}, {gs_pct}%, Fitness: {gs_score}'
    if out is None:
        print(gs_summary)
    else:
        out.write(gs_summary + '\n')

    # Unscheduled observations.
    unscheduled = [str(o) for o in range(observations.num_obs) if o not in final_schedule]
    if len(unscheduled) > 0:
        unscheduled_summary = f'\nUnscheduled observations: {", ".join(unscheduled)}'
        if out is None:
            print(unscheduled_summary)
        else:
            out.write(unscheduled_summary + '\n')


def print_observations(obs: Observations, timeslots: TimeSlots) -> None:
    """
    Output the list of observations.
    Prior to doing this, calculate_priority should be called.
    :param obs: the Observations object containing the observations
    :param slots: the TimeSlots object containing timeslot information
    """
    print("Observations:")
    print("Index  ObsTime Priority  StartSlots")
    for idx in range(obs.num_obs):
        prev_site = 0
        ss = []
        for slot in obs.start_slots[idx]:
            slot_idx = slot.timeslot_idx
            slot_metric = slot.metric_score
            site, site_slot = divmod(slot_idx, timeslots.num_timeslots_per_site)
            if site != prev_site:
                ss.append('  |||  ')
                prev_site = site
            ss.append(f"{Resource(site).name}{site_slot}({slot_metric})")
        print(f"{idx:>5}  {int(obs.obs_time[idx]):>7} {obs.priority[idx]:>8}  "
              f"{' '.join(ss)}")



