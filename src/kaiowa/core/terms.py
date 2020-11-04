from __future__ import annotations

import abc
from typing import Any, TYPE_CHECKING

from kaiowa.core.criteria import Constant, And, Equal, Not, NotEqual, Or

if TYPE_CHECKING:
    from kaiowa.core.selectables import Selectable


class Term(abc.ABC):
    """
    A Term is anything that can be used to filter or manipulate
    the resulting rows of the current Query.

    Whatever is used to identify the Term, it **MUST** represent a `Column`
    of the selectable used in the Query. The identifier is used to name
    the column in the Query Result returned by the database.

    The terms supported by Kaiowa ORM are the following::

        - Scalar: Simple scalar value.
        - Field: Representation of a column of the selectable.
        - Operators: Operators used to filter the Query results.
        - Functions: Functions that will return a manipulated result.

    If the Term is a Function, it **MUST** be aliased by the name of the column
    used by it or, if more than one column is used, it **MUST** have a name
    that will not cause collisions with the other Terms of the Query.
    """

    def __eq__(self, value: Any) -> Equal:
        return Equal(self, self._parse_value(value))

    def __ne__(self, value: Any) -> NotEqual:
        return NotEqual(self, self._parse_value(value))

    def __and__(self, value: Any) -> And:
        return And(self, self._parse_value(value))

    def __or__(self, value: Any) -> Or:
        return Or(self, self._parse_value(value))

    def __invert__(self) -> Not:
        return Not(self)

    @abc.abstractmethod
    def __str__(self) -> str:
        """
        Returns the formatted SQL of the Term, already containing the alias
        used to identity the Term on the filtering step of the Query.

        :return: Formatted SQL statement of the Term.
        :rtype: str
        """

    def _parse_value(self, value: Any) -> str:
        if isinstance(value, (bool, int, float, str)):
            return Constant(value)

        return value


class Field(Term):
    def __init__(self, name: str, parent: Selectable) -> None:
        super().__init__()

        self.name = name
        self.parent = parent

    def __str__(self) -> str:
        return f"{self.parent.alias}.{self.name}"
