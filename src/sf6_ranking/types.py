from typing import Literal

CharacterFilters = Literal["all", "max_mr", "selected_char", "specific_char"]

Characters = Literal[
    "luke",
    "jamie",
    "manon",
    "kimberly",
    "marisa",
    "lily",
    "jp",
    "juri",
    "deejay",
    "cammy",
    "ryu",
    "honda",
    "blanka",
    "guile",
    "ken",
    "chun-li",
    "zangief",
    "dhalsim",
    "rashid",
    "aki",
    "ed",
    "gouki",
]


Region = Literal[
    "all",
    "africa",
    "asia",
    "europe",
    "south_america",
    "north_america",
    "oceania",
    "specific_region",
]

Platform = Literal["all", "same_platform"]
