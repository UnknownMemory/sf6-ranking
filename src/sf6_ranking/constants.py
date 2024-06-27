from enum import IntEnum


class CharacterFiltersEnum(IntEnum):
    all = 1
    max_mr = 2
    selected_char = 3
    specific_char = 4


class RegionEnum(IntEnum):
    all = 0
    africa = 1
    asia = 2
    europe = 3
    south_america = 4
    north_america = 5
    oceania = 6
    specific_region = 7


class PlatformEnum(IntEnum):
    all = 1
    same_platform = 2


class SeasonEnum(IntEnum):
    current = 1
    previous = 2
