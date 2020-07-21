# input_parameters.py
# By Sebastian Raaphorst, 2020.

from enum import IntEnum
from typing import List

import numpy as np


class Resource(IntEnum):
    GN = 0
    GS = 1


# An alias for priority. Right now we use a simple int as a priority.
Priority = int

# The duration of a timeslot. We use 5 * 60 s = 300 s, or 5 minutes.
TIMESLOT_LENGTH = 5 * 60

# The number of timeslots per site. We schedule currently 30 mins per site.
NUM_TIMESLOTS_PER_SITE = 6


class TimeSlot:
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


# We store the timeslots as a list so we can access it by index and avoid iteration issues.
TimeSlots = List[TimeSlot]


def create_timeslots() -> TimeSlots:
    """
    Create the timeslots for scheduling.
    For each resource, we begin at time 0 and create a timeslot.
    We then increment by TIMESLOT_LENGTH and create another timeslot.
    We continue to create timeslots until we have the specified number for each resource.

    :return: a list of timeslots
    """
    slots = []
    for r in Resource:
        for idx in range(NUM_TIMESLOTS_PER_SITE):
            slots.append(TimeSlot(r, idx * TIMESLOT_LENGTH))
    return slots


def get_time_slot(resource: Resource, index: int, timeslots: TimeSlots) -> TimeSlot:
    """
    Given a resource and an index into its timeslots, return the corresponding timeslot.
    :param resource: the Resource
    :param index: the index, in [0, NUM_TIMESLOTS_PER_SITE]
    :param timeslots: the list of TimeSlots
    :return: the TimeSlot, if it exists
    :except: ValueError if the index condition is violated
    """
    return timeslots[resource * NUM_TIMESLOTS_PER_SITE + index]


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
        self.start_slot_idx = []
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

    def add_obs(self, band: str, start_slot_idx: List[int], obs_time: float,
                allocated_time=None):
        assert (allocated_time != 0)
        self.band = np.append(self.band, band)
        self.start_slot_idx.append(start_slot_idx)
        self.used_time = np.append(self.used_time, 0)
        self.allocated_time = np.append(self.allocated_time, obs_time if allocated_time is None else allocated_time)
        self.obs_time = np.append(self.obs_time, obs_time)
        self.num_obs += 1

    def is_done(self, id: int) -> bool:
        return self.used_time[id] >= self.obs_time[id]

    def calculate_completion(self):
        """
        Calculate the completion of the observations.
        This is a simplification that expects the observation to take up (at least) the entire allocated time.
        """
        time = (self.used_time + self.obs_time) / self.allocated_time
        self.completed = np.where(time > 1., 1., time)

    def __len__(self):
        return self.num_obs

    def calculate_priority(self):
        """
        Compute the priority as a function of completeness fraction and band for the objective function.

        Parameters
            completion: array/list of program completion fractions
            band: integer array of bands for each program

        By Bryan Miller, 2020.
        """
        # Calculate the completion for all observations.
        self.calculate_completion()

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


def print_observations(obs: Observations):
    """
    Output the list of observations.
    Prior to doing this, calculate_priority should be called.
    :param obs: the Observations object containing the observations
    """
    # For padding, get the highest alloclen.
    priolenmax = max([len("%.4f" % int(obs.priority[idx])) for idx in range(obs.num_obs)])

    print("Observations:")
    print("Index  Band  ObsTime  AllocTime  Priority  StartSlots")
    for idx in range(obs.num_obs):
        ss = []
        for slot_idx in obs.start_slot_idx[idx]:
            site, site_slot = divmod(slot_idx, NUM_TIMESLOTS_PER_SITE)
            ss.append("%s%s" % (Resource(site).name, site_slot))
        priolen = len("%.4f" % int(obs.priority[idx]))
        print("%5s  %4s  %7s  %9s  %.4f%s   %s" %
              (idx, obs.band[idx], int(obs.obs_time[idx]), int(obs.allocated_time[idx]),
               obs.priority[idx], (" " * (priolenmax - priolen)),
               ' '.join(ss)))


if __name__ == '__main__':
    print("Creating %d timeslots of length %d s each for each site...\n" % (NUM_TIMESLOTS_PER_SITE, TIMESLOT_LENGTH))
    slots = create_timeslots()
    for r in Resource:
        print("%s slots" % r)
        print("-----------------")
        for s in range(NUM_TIMESLOTS_PER_SITE):
            timeslot = get_time_slot(r, s, slots)
            print("%d s -> %d s" % (timeslot.start_time, timeslot.start_time + TIMESLOT_LENGTH - 1))
        print()


