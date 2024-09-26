from abc import ABC
import typing as tp
from dataclasses import dataclass
T = tp.TypeVar('T')


class Result(ABC, tp.Generic[T]):
    pass


@dataclass
class Success(Result[T]):
    value: T


@dataclass
class Failure(Result[T]):
    errorMessage: str
