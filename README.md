MSSQLDelete
===========
Creates a cursor object for an incoming signal and executes one command per signal.

Properties
----------
- **connection**: user_id, password, server, port, database, mars
- **enrich**: enable signal enrichment
- **id**: block id
- **table**: database table to be affected
- **conditions**: search condition

Inputs
------
- **default**: any list of signals

Outputs
-------
- **default**: A signal with the number of rows deleted

Commands
--------
None

Dependencies
------------
- pyodbc
- [Microsoft ODBC Driver 17 for SQL Server](https://www.microsoft.com/en-us/download/details.aspx?id=56567)

***

MSSQLInsert
===========
Creates a cursor object for every list of signals, and executes one query per signal. Changes are committed automatically for each list of signals. When changes are committed, all active cursors (i.e. lists of signals) for that connection (i.e. instance of the block) are committed simultaneously. To avoid this behavior use multiple instances of the block.

Properties
----------
- **connection**: user_id, password, server, port, database, mars
- **enrich**: enable signal enrichment
- **id**: block id
- **table**: database table to be affected
- **row**: record to be inserted as `{key: value}` pairs

Inputs
------
- **default**: A list of signals with one record to insert per signal

Outputs
-------
- **default**: One signal per list of signals processed, with the attribute `inserted` containing the number of records inserted

Commands
--------
None

Dependencies
------------
- pyodbc
- [Microsoft ODBC Driver 17 for SQL Server](https://www.microsoft.com/en-us/download/details.aspx?id=56567)

***

MSSQLQuery
==========
Creates a cursor object for every list of signals, and executes one query per signal returning all matching records in a new list of signals.

Properties
----------
- **connection**: user_id, password, server, port, database, mars
- **enrich**: enable signal enrichment
- **id**: block id
- **table**: database table to be affected
- **conditions**: conditions to be met for items to be retrieved

Inputs
------
- **default**: Any list of signals

Outputs
-------
- **No Results**: One signal, with a return value null
- **Results**: One signal per list of signals processed, with the attribute inserted containing the number of records inserted

Commands
--------
None

Dependencies
------------
- pyodbc
- [Microsoft ODBC Driver 17 for SQL Server](https://www.microsoft.com/en-us/download/details.aspx?id=56567)

***

MSSQLUpdate
===========
Creates a cursor object for every list of signals, and executes one update per signal

Properties
----------
- **connection**: user_id, password, server, port, database, mars
- **enrich**: enable signal enrichment
- **id**: block id
- **table**: database table to be affected
- **conditions**: conditions to be met for records to be updated
- **column_values**: list of values to be updated

Inputs
------
- **default**: any list of signals

Outputs
-------
- **default**: the number of rows updated

Commands
--------
None

***

MSSQLRawQuery
=============
Creates a cursor object for every list of signals, and executes one query per signal. Changes are committed automatically for each list of signals. When changes are committed, all active cursors (i.e. lists of signals) for that connection (i.e. instance of the block) are committed simultaneously. To avoid this behavior use multiple instances of the block.

Properties
----------
- **connection**: user_id, password, server, port, database, mars
- **enrich**: enable signal enrichment
- **id**: block id
- **query**: parameterized SQL query to execute
- **parameters**: list of parameters that will be substituted into the query

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

