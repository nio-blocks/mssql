MSSQLDelete
===========
Creates a cursor object for an incoming signal and executes one command per signal.

Properties
----------
- **command**: 
- **credentials**: UID and PWD used for database authentication
- **database**: name of databse to connect to
- **id**: block id
- **mars**: Enable MARS for SQL database connections
- **port**: server port number
- **server**: server hostname or address

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
- **credentials**: UID and PWD used for database authentication
- **database**: name of database to connect to
- **enrich**: enable signal enrichment
- **id**: 
- **mars**: Enable MARS for SQL database connections
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
- pyodbc
- [Microsoft ODBC Driver 17 for SQL Server](https://www.microsoft.com/en-us/download/details.aspx?id=56567)

***

MSSQLQuery
==========
Creates a cursor object for every list of signals, and executes one query per signal returning all matching records in a new list of signals.

Properties
----------
- **credentials**: UID and PWD used for database authentication
- **database**: name of database to connect to
- **enrich**: enable signal enrichment
- **id**: block id
- **mars**: Enable MARS for SQL database connections
- **port**: server port number
- **query**: SQL query to execute
- **server**: server hostname or address

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
- **credentials**: UID and PWD used for database authentication
- **database**: name of database to connect to
- **id**: block id
- **mars**: Enable MARS for SQL database connections
- **port**: server port number
- **server**: server hostname or address
- **update**: update command to be executed against the SQL database

Inputs
------
- **default**: any list of signals

Outputs
-------
- **default**: the number of rows updated

Commands
--------
None

