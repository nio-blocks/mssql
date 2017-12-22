MSSQLInsert
===========
Creates a cursor object for every list of signals, and executes one query per signal. Changes are committed automatically for each list of signals. When changes are committed, all active cursors (i.e. lists of signals) for that connection (i.e. instance of the block) are committed simultaneously. To avoid this behavior use multiple instances of the block.

Properties
----------
- **credentials**: UID and PWD used for database authentication
- **database**: name of database to connect to
- **port**: server port number
- **row**: record to be inserted as `{key: value}` pairs
- **server**: server hostname or address
- **table**: database table to be affected

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
pyodbc  
[Microsoft ODBC Driver 13 for SQL Server](https://www.microsoft.com/en-us/download/details.aspx?id=50420)

MSSQLQuery
==========
Creates a cursor object for every list of signals, and executes one query per signal returning all matching records in a new list of signals.

Properties
----------
- **credentials**: UID and PWD used for database authentication
- **database**: name of database to connect to
- **port**: server port number
- **query**: SQL query to execute
- **server**: server hostname or address

Inputs
------
- **default**: Any list of signals

Outputs
-------
- **default**: One list of signals for every query executed, where each signal contains one record as `{key: value}` pairs

Commands
--------
None

Dependencies
------------
pyodbc  
[Microsoft ODBC Driver 13 for SQL Server](https://www.microsoft.com/en-us/download/details.aspx?id=50420)

