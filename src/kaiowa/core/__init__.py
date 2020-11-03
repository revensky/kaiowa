"""
This module contains the Core functionalities of Kaiowa ORM,
especially related to the Query Building functionalities.

Kaiowa Core is segregated in the following modules.

1. Selectables - Defines the entities used to build the SQL queries, such as::
    - Table: Abstract representation of a database table. It accepts a name,
        an alias via the method :meth:`as_`, and supports the standard SQL operations,
        e.g. SELECT, DELETE, etc.
    - Field: Abstract representation of a table column. It has methods regarding
        to query filters, such as `IN`, `NOT IN`, etc.
    - Query: Stateful object representing a query to be run against the database.
        A query supports **ONLY ONE** operation per instance. So, if the application
        defines something like

        .. code-block:: python

            users = Table("users")
            query = Query().select().from_(users).delete()

        the operation defined in the Query will be `DELETE`.

2. Terms - Defines the wrappers for constant values and query criteria,
    such as AND, OR, etc.
"""
