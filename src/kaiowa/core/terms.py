from __future__ import annotations

import abc
from typing import Any, Sequence, TYPE_CHECKING

from kaiowa.core.criteria import (
    Addition,
    And,
    Between,
    Distinct,
    Division,
    Equal,
    False_,
    Filterable,
    GreaterEqual,
    GreaterThan,
    ILike,
    In,
    IsNotNull,
    IsNull,
    LessEqual,
    LessThan,
    Like,
    Multiplication,
    Negative,
    Not,
    NotBetween,
    NotDistinct,
    NotEqual,
    NotFalse,
    NotILike,
    NotIn,
    NotLike,
    NotTrue,
    NotUnknown,
    Or,
    Subtraction,
    True_,
    Unknown,
)

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

    @abc.abstractmethod
    def __str__(self) -> str:
        """
        Returns the formatted SQL of the Term, already containing the alias
        used to identity the Term on the filtering step of the Query.

        :return: Formatted SQL statement of the Term.
        :rtype: str
        """

    def __eq__(self, value: Filterable) -> Equal:
        return Equal(self, value)

    def __ne__(self, value: Filterable) -> NotEqual:
        return NotEqual(self, value)

    def __lt__(self, value: Filterable) -> LessThan:
        return LessThan(self, value)

    def __le__(self, value: Filterable) -> LessEqual:
        return LessEqual(self, value)

    def __gt__(self, value: Filterable) -> GreaterThan:
        return GreaterThan(self, value)

    def __ge__(self, value: Filterable) -> GreaterEqual:
        return GreaterEqual(self, value)

    def __and__(self, value: Filterable) -> And:
        return And(self, value)

    def __or__(self, value: Filterable) -> Or:
        return Or(self, value)

    def __invert__(self) -> Not:
        return Not(self)

    def __neg__(self) -> Negative:
        return Negative(self)

    def __pos__(self) -> Term:
        return self

    def __add__(self, other: Filterable) -> Addition:
        return Addition(self, other)

    def __sub__(self, other: Filterable) -> Subtraction:
        return Subtraction(self, other)

    def __mul__(self, other: Filterable) -> Multiplication:
        return Multiplication(self, other)

    def __truediv__(self, other: Filterable) -> Division:
        return Division(self, other)

    def __radd__(self, other: Filterable) -> Addition:
        return Addition(other, self)

    def __rsub__(self, other: Filterable) -> Subtraction:
        return Subtraction(other, self)

    def __rmul__(self, other: Filterable) -> Multiplication:
        return Multiplication(other, self)

    def __rtruediv__(self, other: Filterable) -> Division:
        return Division(other, self)

    def is_null(self) -> IsNull:
        return IsNull(self)

    def not_null(self) -> IsNotNull:
        return IsNotNull(self)

    def in_(self, values: Sequence[Any]) -> In:
        return In(self, values)

    def not_in(self, values: Sequence[Any]) -> NotIn:
        return NotIn(self, values)

    def like(self, value: str) -> Like:
        return Like(self, value)

    def not_like(self, value: str) -> NotLike:
        return NotLike(self, value)

    def ilike(self, value: str) -> ILike:
        return ILike(self, value)

    def not_ilike(self, value: str) -> NotILike:
        return NotILike(self, value)

    def between(self, start: Any, end: Any) -> Between:
        return Between(self, start, end)

    def not_between(self, start: Any, end: Any) -> NotBetween:
        return NotBetween(self, start, end)

    def distinct(self, value: Any) -> Distinct:
        return Distinct(self, value)

    def not_distinct(self, value: Any) -> NotDistinct:
        return NotDistinct(self, value)

    def true(self) -> True_:
        return True_(self)

    def not_true(self) -> NotTrue:
        return NotTrue(self)

    def false(self) -> False_:
        return False_(self)

    def not_false(self) -> NotFalse:
        return NotFalse(self)

    def unknown(self) -> Unknown:
        return Unknown(self)

    def not_unknown(self) -> NotUnknown:
        return NotUnknown(self)


class Field(Term):
    """
    Representation of a Selectable's Column.

    :param name: Name of the Column.
    :type name: str

    :param parent: Selectable (Table/SubQuery) to whom the Field pertains to.
    :type parent: Selectable
    """

    def __init__(self, name: str, parent: Selectable) -> None:
        self.name = name
        self.parent = parent

    def __str__(self) -> str:
        return f"{self.parent.alias}.{self.name}"
