from enum import IntEnum


class SubjectTypes(IntEnum):
    HOMEROOM = 0
    ELA = 1
    MATH = 2
    CIVICS = 3
    SCIENCE = 4
    ESL = 5
    NUMERACY = 6
    # HOMEROOM = 7

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class TruancyTypes(IntEnum):
    ABSENT = 0
    TARDY = 1
    SKIP = 2

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

