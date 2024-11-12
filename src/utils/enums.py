from enum import StrEnum, auto


class SubmissionStatus(StrEnum):
    PENDING = auto()
    ACCEPTED = auto()
    WRONG_ANSWER = auto()
    TIME_LIMIT_EXCEEDED = auto()
    MEMORY_LIMIT_EXCEEDED = auto()
    INTERNAL_ERROR = auto()
    COMPILATION_ERROR = auto()
    RUNTIME_ERROR = auto()


class ContestProgress(StrEnum):
    NOT_STARTED = auto()
    IN_PROGRESS = auto()
    FINISHED = auto()
    