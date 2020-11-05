from __future__ import annotations

import abc
from typing import Any, Sequence, Union, TYPE_CHECKING

from kaiowa.core.utils import quote

if TYPE_CHECKING:
    from kaiowa.core.selectables import Term


Filterable = Union["Criterion", "Term"]


class Criterion(abc.ABC):
    """
    Representation of an abstract criterion of the SQL Query.

    It usually represents the operation filters presented in the :meth:`where` method.
    """

    @abc.abstractmethod
    def __str__(self) -> str:
        """
        Returns the formatted SQL statement of the criterion.

        :return: Criterion's SQL statement.
        :rtype: str
        """

    def __eq__(self, other: Filterable) -> Equal:
        return Equal(self, other)

    def __ne__(self, other: Filterable) -> NotEqual:
        return NotEqual(self, other)

    def __lt__(self, other: Filterable) -> LessThan:
        return LessThan(self, other)

    def __le__(self, other: Filterable) -> LessEqual:
        return LessEqual(self, other)

    def __gt__(self, other: Filterable) -> GreaterThan:
        return GreaterThan(self, other)

    def __ge__(self, other: Filterable) -> GreaterEqual:
        return GreaterEqual(self, other)

    def __and__(self, other: Filterable) -> And:
        return And(self, other)

    def __or__(self, other: Filterable) -> Or:
        return Or(self, other)

    def __invert__(self) -> Not:
        return Not(self)

    def __neg__(self) -> Negative:
        return Negative(self)

    def __pos__(self) -> Criterion:
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

    def _parse_value(self, value: Filterable) -> str:
        if isinstance(value, (bool, int, float, str)):
            return Constant(value)

        return value


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


class Unary(Criterion):
    def __init__(self, term: Union[Term, Criterion]) -> None:
        self.term = term


class Binary(Criterion):
    def __init__(
        self, left: Union[Term, Criterion], right: Union[Term, Criterion]
    ) -> None:
        self.left = left
        self.right = right


class Equal(Binary):
    def __str__(self) -> str:
        self.right = self._parse_value(self.right)
        return f"{str(self.left)} = {str(self.right)}"


class NotEqual(Binary):
    def __str__(self) -> str:
        return f"{str(self.left)} <> {str(self.right)}"


class LessThan(Binary):
    def __str__(self) -> str:
        return f"{str(self.left)} < {str(self.right)}"


class LessEqual(Binary):
    def __str__(self) -> str:
        return f"{str(self.left)} <= {str(self.right)}"


class GreaterThan(Binary):
    def __str__(self) -> str:
        return f"{str(self.left)} > {str(self.right)}"


class GreaterEqual(Binary):
    def __str__(self) -> str:
        return f"{str(self.left)} >= {str(self.right)}"


class And(Binary):
    def __str__(self) -> str:
        return f"({str(self.left)}) AND ({self.right})"


class Or(Binary):
    def __str__(self) -> str:
        return f"({str(self.left)}) OR ({str(self.right)})"


class Not(Unary):
    def __str__(self) -> str:
        return f"NOT ({str(self.term)})"


class Negative(Unary):
    def __str__(self) -> str:
        return f"-{str(self.term)}"


class Addition(Binary):
    def __str__(self) -> str:
        return f"({str(self.left)}) + ({str(self.right)})"


class Subtraction(Binary):
    def __str__(self) -> str:
        return f"({str(self.left)}) - ({str(self.right)})"


class Multiplication(Binary):
    def __str__(self) -> str:
        return f"({str(self.left)}) * ({str(self.right)})"


class Division(Binary):
    def __str__(self) -> str:
        return f"({str(self.left)}) / ({str(self.right)})"


class IsNull(Criterion):
    def __init__(self, term: Term) -> None:
        self.term = term

    def __str__(self) -> str:
        return f"{str(self.term)} IS NULL"


class IsNotNull(Criterion):
    def __init__(self, term: Term) -> None:
        self.term = term

    def __str__(self) -> str:
        return f"{str(self.term)} IS NOT NULL"


class In(Criterion):
    def __init__(self, left: Term, right: Sequence[Any]) -> None:
        self.left = left
        self.right = right

    def __str__(self) -> str:
        values = [quote(value) for value in self.right]
        return f"{str(self.left)} IN ({','.join(values)})"


class NotIn(Criterion):
    def __init__(self, left: Term, right: Sequence[Any]) -> None:
        self.left = left
        self.right = right

    def __str__(self) -> str:
        values = [quote(value) for value in self.right]
        return f"{str(self.left)} NOT IN ({','.join(values)})"


class Like(Criterion):
    def __init__(self, term: Term, expr: str) -> None:
        self.term = term
        self.expr = expr

    def __str__(self) -> str:
        return f"{str(self.term)} LIKE {quote(self.expr)}"


class NotLike(Criterion):
    def __init__(self, term: Term, expr: str) -> None:
        self.term = term
        self.expr = expr

    def __str__(self) -> str:
        return f"{str(self.term)} NOT LIKE {quote(self.expr)}"


class ILike(Criterion):
    def __init__(self, term: Term, expr: str) -> None:
        self.term = term
        self.expr = expr

    def __str__(self) -> str:
        return f"{str(self.term)} ILIKE {quote(self.expr)}"


class NotILike(Criterion):
    def __init__(self, term: Term, expr: str) -> None:
        self.term = term
        self.expr = expr

    def __str__(self) -> str:
        return f"{str(self.term)} NOT ILIKE {quote(self.expr)}"


class Between(Criterion):
    def __init__(self, term: Term, start: Any, end: Any) -> None:
        self.term = term
        self.start = start
        self.end = end

    def __str__(self) -> str:
        return f"{str(self.term)} BETWEEN {self.start} AND {self.end}"


class NotBetween(Criterion):
    def __init__(self, term: Term, start: Any, end: Any) -> None:
        self.term = term
        self.start = start
        self.end = end

    def __str__(self) -> str:
        return f"{str(self.term)} NOT BETWEEN {self.start} AND {self.end}"


class Distinct(Criterion):
    def __init__(self, left: Term, right: Filterable) -> None:
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"{str(self.left)} IS DISTINCT FROM {str(self.right)}"


class NotDistinct(Criterion):
    def __init__(self, left: Term, right: Filterable) -> None:
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"{str(self.left)} IS NOT DISTINCT FROM {str(self.right)}"


class True_(Unary):
    def __str__(self) -> str:
        return f"{str(self.term)} IS TRUE"


class NotTrue(Unary):
    def __str__(self) -> str:
        return f"{str(self.term)} IS NOT TRUE"


class False_(Unary):
    def __str__(self) -> str:
        return f"{str(self.term)} IS FALSE"


class NotFalse(Unary):
    def __str__(self) -> str:
        return f"{str(self.term)} IS NOT FALSE"


class Unknown(Unary):
    def __str__(self) -> str:
        return f"{str(self.term)} IS UNKNOWN"


class NotUnknown(Unary):
    def __str__(self) -> str:
        return f"{str(self.term)} IS NOT UNKNOWN"
