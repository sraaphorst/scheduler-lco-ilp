# input_parameters.py
# By Sebastian Raaphorst, 2020.

from enum import IntEnum
from typing import List
from math import ceil


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


class Observation:
    def __init__(self, priority: Priority, observation_length: int, start_slot_idxs: List[int]):
        """
        Basic representation of an observation.
        In this scenario, observations cannot be interrupted, i.e. they must be completed entirely within
        consecutive time slots. Additionally, as a result, observation priorities do not change.

        :param priority: the priority of the observation: higher priority observations are more likely to be scheduled
        :param observation_length: the length of the observation, in seconds
        :param start_slot_idxs: the permissible slots for the observation to start: the observation will consume subsequent
                            time slots until it is done, i.e. has run for observation_length. These should be indices.
        """
        self.priority = priority
        self.observation_length = observation_length
        self.start_slots_idxs = start_slot_idxs

        # We calculate the number of time slots necessary to complete the observation.
        # If if cannot be completed in an exact number of time slots, round up through ceil.
        self.needed_timeslots = int(ceil(observation_length / TIMESLOT_LENGTH))


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


