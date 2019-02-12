MSSQLQuery
==========
Creates a cursor object for every list of signals, and executes one query per signal. Changes are committed automatically for each list of signals. When changes are committed, all active cursors (i.e. lists of signals) for that connection (i.e. instance of the block) are committed simultaneously. To avoid this behavior use multiple instances of the block.

Properties
----------
- **query**: parameterized SQL query
- **parameters**: list of parameters to substitute into the query
- **connection**: userid, password, server, port, database, mars
- **id**: block id

Inputs
------
- **default**: any list of signals

Outputs
-------
- **results**: A signal with an array of results
- **no_results**: A signal with a null results key

Commands
--------
None

Dependencies
------------
- pyodbc
- [Microsoft ODBC Driver 17 for SQL Server](https://www.microsoft.com/en-us/download/details.aspx?id=56567)
