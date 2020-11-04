from __future__ import annotations

import abc
from typing import Any, Union, TYPE_CHECKING

from kaiowa.core.utils import quote

if TYPE_CHECKING:
    from kaiowa.core.selectables import Term


class Criterion(abc.ABC):
    """
    Representation of an abstract criterion of the SQL Query.

    It usually represents the operation filters presented in the :meth:`where` method.
    """

    def __eq__(self, other: Criterion) -> Equal:
        return Equal(self, other)

    def __ne__(self, other: Criterion) -> NotEqual:
        return NotEqual(self, other)

    def __and__(self, other: Criterion) -> And:
        return And(self, other)

    def __or__(self, other: Criterion) -> Or:
        return Or(self, other)

    def __invert__(self) -> Not:
        return Not(self)

    @abc.abstractmethod
    def __str__(self) -> str:
        """
        Returns the formatted SQL statement of the criterion.

        :return: Criterion's SQL statement.
        :rtype: str
        """


class Precedence(Criterion):
    def __init__(self, criterion: Criterion) -> None:
        self.criterion = criterion

    def __str__(self) -> str:
        return f"({self.criterion})"


class Constant(Criterion):
    def __init__(self, value: Union[int, float, bool, str]) -> None:
        if isinstance(value, bool):
            self.value = str(value).upper()
        elif isinstance(value, str):
            quote_char = '"' if "'" in value else "'"
            self.value = quote(value, quote_char)
        else:
            self.value = str(value)

    def __str__(self) -> str:
        return self.value


class Equal(Criterion):
    def __init__(self, left: Term, right: Any) -> None:
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"{str(self.left)} = {str(self.right)}"


class NotEqual(Criterion):
    def __init__(self, left: Term, right: Any) -> None:
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"{str(self.left)} <> {str(self.right)}"


class And(Criterion):
    def __init__(
        self, left: Union[Term, Criterion], right: Union[Term, Criterion]
    ) -> None:
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"{str(self.left)} AND {self.right}"


class Or(Criterion):
    def __init__(
        self, left: Union[Term, Criterion], right: Union[Term, Criterion]
    ) -> None:
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"{str(self.left)} OR {str(self.right)}"


class Not(Criterion):
    def __init__(self, term: Term) -> None:
        self.term = term

    def __str__(self) -> str:
        return f"NOT {str(self.term)}"
