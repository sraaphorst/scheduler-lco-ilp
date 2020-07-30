# common.py
# By Sebastian Raaphorst, 2020.
# This file defines the objects that manage time slots and observations, and
# the primary output formatting.

from enum import IntEnum
from typing import List, Union, Tuple, Callable
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
    def __init__(self, timeslot_length: int = 5 * 60, num_timeslots_per_site: int = 6):
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
            for idx in range(num_timeslots_per_site):
                self.timeslots.append(TimeSlot(r, idx * timeslot_length))

    def get_time_slot(self, resource: Resource, index: int) -> TimeSlot:
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
        band - an array of band ('1', '2', '3', '4' as per Bryan's representation below) for observation i
        completed - the current completion fraction
        used_time - the time used so far
        allocation_time - the total time allocation
        obs_time - the length of the observation
        allocated - the time allocated for the observation
        start_slot_idxs - a list of timeslot indices representing what timeslots the observation can
                        can be observed at
        priority - the priority for time slice t
        """
        self.num_obs = 0
        self.band = np.empty((0,), dtype=str)
        self.completed = np.empty((0,), dtype=float)
        self.used_time = np.empty((0,), dtype=float)
        self.allocated_time = np.empty((0,), dtype=float)
        self.obs_time = np.empty((0,), dtype=float)
        self.start_slots = []
        self.priority = np.empty((0,), dtype=float)

        self.params = {'1': {'m1': 1.406, 'b1': 2.0, 'm2': 0.50, 'b2': 0.5, 'xb': 0.8, 'xb0': 0.0, 'xc0': 0.0},
                       '2': {'m1': 1.406, 'b1': 1.0, 'm2': 0.50, 'b2': 0.5, 'xb': 0.8, 'xb0': 0.0, 'xc0': 0.0},
                       '3': {'m1': 1.406, 'b1': 0.0, 'm2': 0.50, 'b2': 0.5, 'xb': 0.8, 'xb0': 0.0, 'xc0': 0.0},
                       '4': {'m1': 0.00, 'b1': 0.0, 'm2': 0.00, 'b2': 0.0, 'xb': 0.8, 'xb0': 0.0, 'xc0': 0.0},
                       }

        # Now spread the metric to avoid band overlaps
        # m2 = {'3': 0.5, '2': 3.0, '1':10.0} # use with b1*r where r=3
        m2 = {'3': 1.0, '2': 6.0, '1': 20.0}  # use with b1 + 5.
        xb = 0.8
        b1 = 0.2
        for band in ['3', '2', '1']:
            b2 = b1 + 5. - m2[band]
            m1 = (m2[band] * xb + b2) / xb ** 2
            self.params[band]['m1'] = m1
            self.params[band]['m2'] = m2[band]
            self.params[band]['b1'] = b1
            self.params[band]['b2'] = b2
            self.params[band]['xb'] = xb
            b1 += m2[band] * 1.0 + b2

    def add_obs(self, band: str, start_slot_idx: List[TS], obs_time: float,
                allocated_time=None) -> None:
        """
        Add an observation to the collection of observations.
        :param band: the band of the observation: a string of 1, 2, or 3
        :param start_slot_idx: a list of TS data objects, which are TimeSlots and metric scores.
        :param obs_time: the observation time
        :param allocated_time: the allocated time
        """
        assert (allocated_time != 0)
        self.band = np.append(self.band, band)
        self.start_slots.append(start_slot_idx)
        self.used_time = np.append(self.used_time, 0)
        self.allocated_time = np.append(self.allocated_time, obs_time if allocated_time is None else allocated_time)
        self.obs_time = np.append(self.obs_time, obs_time)
        self.num_obs += 1

    def is_done(self, id: int) -> bool:
        return self.used_time[id] >= self.obs_time[id]

    def _calculate_completion(self) -> None:
        """
        Calculate the completion of the observations.
        This is a simplification that expects the observation to take up (at least) the entire allocated time.
        """
        time = (self.used_time + self.obs_time) / self.allocated_time
        self.completed = np.where(time > 1., 1., time)

    def __len__(self):
        return self.num_obs

    def calculate_priority(self) -> None:
        """
        Compute the priority as a function of completeness fraction and band for the objective function.

        Parameters
            completion: array/list of program completion fractions
            band: integer array of bands for each program

        By Bryan Miller, 2020.
        """
        # Calculate the completion for all observations.
        self._calculate_completion()

        nn = len(self.completed)
        metric = np.zeros(nn)
        for ii in range(nn):
            sband = str(self.band[ii])

            # If Band 3, then the Band 3 min fraction is used for xb
            if self.band[ii] == 3:
                xb = 0.8
            else:
                xb = self.params[sband]['xb']

            # Determine the intercept for the second piece (b2) so that the functions are continuous
            b2 = self.params[sband]['b2'] + self.params[sband]['xb0'] + self.params[sband]['b1']

            # Finally, calculate piecewise the metric.
            if self.completed[ii] == 0.:
                metric[ii] = 0.0
            elif self.completed[ii] < xb:
                metric[ii] = self.params[sband]['m1'] * self.completed[ii] ** 2 + self.params[sband]['b1']
            elif self.completed[ii] < 1.0:
                metric[ii] = self.params[sband]['m2'] * self.completed[ii] + b2
            else:
                metric[ii] = self.params[sband]['m2'] * 1.0 + b2 + self.params[sband]['xc0']
        self.priority = metric


def print_schedule(timeslots: TimeSlots, observations: Observations,
                   final_schedule: Schedule, final_score: Score) -> None:
    """
    Given the execution of a call to schedule, print the results.
    :param timeslots: the TimeSlots object
    :param observations: the Observations object
    :param final_schedule: the final schedule returned from schedule
    :param final_score: the final score returned from schedule
    """
    for site in Resource:
        print('Schedule for %s:' % site.name)
        print('\tTSIdx    ObsIdx')
        for ts_offset in range(timeslots.num_timeslots_per_site):
            ts_idx = ts_offset + site.value * timeslots.num_timeslots_per_site
            if final_schedule[ts_idx] is not None:
                print(f'\t    {ts_offset}         {final_schedule[ts_idx]}')
    print(f'Score: {final_score}')

    # Unschedulable observations.
    unschedulable = [str(o) for o in range(observations.num_obs) if o not in final_schedule]
    if len(unschedulable) > 0:
        print(f'\nUnschedulable observations: {", ".join(unschedulable)}')


def print_observations(obs: Observations, timeslots: TimeSlots) -> None:
    """
    Output the list of observations.
    Prior to doing this, calculate_priority should be called.
    :param obs: the Observations object containing the observations
    :param slots: the TimeSlots object containing timeslot information
    """
    print("Observations:")
    print("Index  Band  ObsTime  AllocTime  Priority  StartSlots")
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
        print(f"{idx:>5}  {obs.band[idx]:>4}  {int(obs.obs_time[idx]):>7}  "
              f"{int(obs.allocated_time[idx]):>9}  {obs.priority[idx]:>8}  "
              f"{' '.join(ss)}")


# The Scheduler type
Scheduler = Callable[[TimeSlots, Observations], Tuple[Schedule, Score]]


if __name__ == '__main__':
    timeslots = TimeSlots()
    print(f"Created {timeslots.num_timeslots_per_site} timeslots of length "
          f"{timeslots.timeslot_length} s each for each site...\n")
    for r in Resource:
        print(f"{r} timeslots")
        print("-----------------")
        for s in range(timeslots.num_timeslots_per_site):
            timeslot = timeslots.get_time_slot(r, s)
            print(f"{timeslot.start_time} s -> {timeslot.start_time + timeslots.timeslot_length - 1} s")
        print()


