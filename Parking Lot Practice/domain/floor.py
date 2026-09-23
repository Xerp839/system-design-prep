from .parking_slot import ParkingSlot
from typing import List, Optional


class Floor:

    def __init__(self, floor_number: int):
        self.floor_number = floor_number
        self.slots : list[ParkingSlot] = []


    def __str__(self):
        return f"Floor {self.floor_number} ({len(self.slots)}) Slots"