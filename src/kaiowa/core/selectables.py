from __future__ import annotations

import abc
from enum import Enum
from typing import Callable, Sequence

from kaiowa.core.criteria import Criterion
from kaiowa.core.terms import Term, Field
from kaiowa.core.utils import make_alias


class JoinTypes(str, Enum):
    join = "JOIN"
    inner_join = "INNER JOIN"
    outer_join = "OUTER JOIN"
    left_join = "LEFT JOIN"
    right_join = "RIGHT JOIN"
    left_outer_join = "LEFT OUTER JOIN"
    right_outer_join = "RIGHT OUTER JOIN"
    full_outer_join = "FULL OUTER JOIN"
    cross_join = "CROSS JOIN"


class Selectable(abc.ABC):
    """
    Base class for selectable entities.

    A selectable entity is anything that can be used to execute a query upon.
    The defined selectables supported by `Kaiowa Core` are::

        - Table: A table is a collection of columns used to store data closely
            related to an application entity.
        - Subquery(Query): A subquery is a previous query that will have its results
            used in the parent query; it can be considered a virtual table.

    Selectables **MUST** be able to have its internal SQL statement parsed to be used
    by another selectable in a query. To do this, the selectable **MUST** implement the
    method :meth:`get_sql`, that **MUST** return a string containing its SQL with all
    the aliases and particularities already well established and formatted.

    Whenever an attribute is not found at the selectable, it **WILL** return
    a `Field` instance containing the attribute as the Field's name and the
    selectable as its entity.
    """

    # Defines the alias of the Selectable.
    _alias: str = None

    def __getattr__(self, key: str) -> Field:
        """
        Returns a Field instance of the requested key,
        with the current selectable as its parent.

        :param key: Name of the Field.
        :type key: str

        :return: Requested attribute as a Field instance.
        :rtype: Field
        """

        return Field(key, self)

    @abc.abstractmethod
    def __str__(self) -> str:
        """
        Returns the formatted SQL statement of the selectable, already formatted
        to contain the alias or the name of the selectable as the prefix of its
        Fields in the necessary case.

        :return: Formatted SQL statement.
        :rtype: str
        """

    @property
    def alias(self) -> str:
        return self._alias


class Table(Selectable):
    """
    A Table represents a "real-world" entity being modeled by the application.

    Since the main purpose of the table is to be a holder of columns,
    its `name` and `alias` attributes names were chosen in order to avoid collision
    with probable names of table fields.

    :param name: Name of the Table.
    :type name: str
    """

    def __init__(self, name: str) -> None:
        self._name = name

    def __repr__(self) -> str:
        return f"<Table: name='{self._name}'; alias='{self._alias}'>"

    def __str__(self) -> str:
        return self._name

    @property
    def alias(self) -> str:
        return self._alias or self._name

    def as_(self, alias: str) -> Table:
        """
        Sets the provided alias as the alias of the Table.

        :param alias: Alias to identify the table.
        :type alias: str

        :return: Current Table instance.
        :rtype: Table
        """

        self._alias = alias
        return self


class Query(Selectable):
    """
    A Query is a statement used to fetch or manipulate data from the database's tables.

    When a Query is used as the object of selection, it becomes a subquery and is
    treated as a `Virtual Table`, where the parameters selected by the Query become
    the virtual columns to be queried by the parent Query.

    Because of this, the Query is treated as both a simple Query used to manipulate data
    **AND** as a Virtual Table (in the form of a subquery) that holds the data.
    """

    # Defines the operation of the current Query.
    _operation: str

    # Defines the Selectable being queried.
    _selectable: Selectable

    # Defines the selectables being joined.
    _joins: list[list[JoinTypes, Selectable, Sequence[Criterion]]]

    # Defines that the select operation MUST return distinct rows only.
    _distinct: bool

    # Defines that the delete operation MUST delete from the selected table only.
    _only: bool

    # Defines the terms to be selected by the Query.
    _terms: list[Term]

    # Defines the criteria to filter the Query.
    _criteria: list[Criterion]

    def __init__(self) -> None:
        self._operation = None
        self._selectable = None
        self._joins = []

        self._distinct = False
        self._only = False

        self._terms = []
        self._criteria = []

    def __repr__(self) -> str:
        return f"<Query: alias='{self.alias}'; operation='{self._operation}'>"

    def __str__(self) -> str:
        """
        Returns the formatted SQL statement of the current Query.

        :return: Formatted SQL statement of the current Query.
        :rtype: str
        """

        builder: Callable[[], str] = getattr(self, f"_make_{self._operation}")
        return builder()

    def as_(self, alias: str) -> Query:
        """
        Sets the alias of the Query.

        :param alias: Alias of the Query.
        :type alias: str

        :return: Current Query.
        :rtype: Query
        """

        self._alias = alias
        return self

    def select(self, *terms: Term) -> Query:
        """
        Sets the operation of the Query as `select` and specifies
        the terms to be used in the Query.

        :param terms: Terms of the Query.
        :type terms: Sequence[Term]

        :return: Current Query.
        :rtype: Query
        """

        self._operation = "select"
        self._terms.extend(terms)
        return self

    def delete(self, only: bool = False) -> Query:
        """
        Sets the operation of the Query as `delete` and, optionally,
        specifies if it will delete from the main table only.

        :param only: Defines if only the main table's rows will be deleted,
            defaults to None.
        :type only: bool, optional

        :return: Current Query.
        :rtype: Query
        """

        self._operation = "delete"
        self._only = only
        return self

    def distinct(self) -> Query:
        """
        Defines if the `select` operation will ignore duplicated rows.

        :return: Current Query.
        :rtype: Query
        """

        self._distinct = True
        return self

    def from_(self, selectable: Selectable) -> Query:
        """
        Defines the selectable to be used by the Query.

        .. note:: The `delete` operation can only use a Table as the selectable.

        :param selectable: Selectable which the Query will run upon.
        :type selectable: Selectable

        :return: Current Query.
        :rtype: Query
        """

        self._selectable = selectable
        return self

    def join(self, selectable: Selectable) -> Query:
        """
        Performs a Join on the specified Selectable.

        :param selectable: Selectable to be joined.
        :type selectable: Selectable

        :return: Current Query.
        :rtype: Query
        """

        self._joins.append([JoinTypes.join, selectable, None])
        return self

    def inner_join(self, selectable: Selectable) -> Query:
        self._joins.append([JoinTypes.inner_join, selectable, None])
        return self

    def outer_join(self, selectable: Selectable) -> Query:
        self._joins.append([JoinTypes.outer_join, selectable, None])
        return self

    def left_join(self, selectable: Selectable) -> Query:
        self._joins.append([JoinTypes.left_join, selectable, None])
        return self

    def right_join(self, selectable: Selectable) -> Query:
        self._joins.append([JoinTypes.right_join, selectable, None])
        return self

    def left_outer_join(self, selectable: Selectable) -> Query:
        self._joins.append([JoinTypes.left_outer_join, selectable, None])
        return self

    def right_outer_join(self, selectable: Selectable) -> Query:
        self._joins.append([JoinTypes.right_outer_join, selectable, None])
        return self

    def full_outer_join(self, selectable: Selectable) -> Query:
        self._joins.append([JoinTypes.full_outer_join, selectable, None])
        return self

    def cross_join(self, selectable: Selectable) -> Query:
        self._joins.append([JoinTypes.cross_join, selectable, None])
        return self

    def on(self, *filters: Criterion) -> Query:
        """
        Defines the fields of the selectables used to perform the joins.

        :param filters: Filters to apply on the join.
        :type filters: Sequence[Criterion]

        :return: Current Query.
        :rtype: Query
        """

        self._joins[-1][2] = filters
        return self

    def where(self, *criteria: Criterion) -> Query:
        """
        Adds a filter to the Query via the Criteria provided in this method.

        :param criteria: Criteria used to filter the Query.
        :type criteria: Sequence[Criterion]

        :return: Current Query.
        :rtype: Query
        """

        self._criteria.extend(criteria)
        return self

    def group_by(self, *criteria: Criterion) -> Query:
        """
        Groups the result of the query using the provided Criteria.

        :param criteria: Criteria used to group the result of the Query.
        :type criteria: Sequence[Criterion]

        :return: Current Query.
        :rtype: Query
        """

        raise NotImplementedError

    def _make_select(self) -> str:
        sql = "SELECT DISTINCT" if self._distinct else "SELECT"

        entity = self._selectable

        alias = entity.alias
        terms = self._parse_terms()

        if isinstance(entity, Table):
            sql += f" {terms} FROM {str(entity)}"

        if isinstance(entity, Query):
            sql += f" {terms} FROM ({str(entity)})"

        sql = make_alias(sql, alias)

        if self._joins:
            sql += self._parse_joins()

        if self._criteria:
            sql += self._parse_criteria()

        return sql

    def _make_delete(self) -> str:
        entity = self._selectable

        sql = (
            f"DELETE FROM ONLY {str(entity)}"
            if self._only
            else f"DELETE FROM {str(entity)}"
        )

        sql = make_alias(sql, entity.alias)

        if self._criteria:
            sql += self._parse_criteria()

        return sql

    def _parse_terms(self) -> str:
        return (
            ",".join([str(term) for term in self._terms])
            or f"{self._selectable.alias}.*"
        )

    def _parse_joins(self) -> str:
        sql = ""

        for join_type, selectable, filters in self._joins:
            # Makes the join call.
            sql += f" {join_type.value} {make_alias(str(selectable), selectable.alias)}"

            if filters:
                # Defines the "ON" filters.
                sql += " ON "
                sql += "".join([str(criterion) for criterion in filters])

        return sql

    def _parse_criteria(self) -> str:
        sql = " WHERE "
        sql += "".join([str(criterion) for criterion in self._criteria])
        return sql
