import pyodbc
from nio.block.base import Block
from nio.properties import (VersionProperty, StringProperty, PropertyHolder, ObjectProperty, IntProperty, BoolProperty)
from nio.util.discovery import not_discoverable

class Connection(PropertyHolder):

    server = StringProperty(title='Server', default='[[MSSQL_SERVER]]', order=1)
    port = IntProperty(title='Port', default='[[MSSQL_PORT]]', order=2)
    database = StringProperty(title='Database', default='[[MSSQL_DB]]', order=3)
    userid = StringProperty(title='User ID', allow_none=True, default='[[MSSQL_USER]]', order=4)
    password = StringProperty(title="Password", allow_none=True, default='[[MSSQL_PWD]]', order=5)
    mars = BoolProperty(title='Enable Multiple Active Result Sets', default=False, order=6)

@not_discoverable
class MSSQLBase(Block):

    version = VersionProperty('1.0.0')
    connection = ObjectProperty(Connection, title='Database Connection', order=1, advanced=True)

    def __init__(self):
        super().__init__()
        self.cnxn = None
        self.cursor = None
        self.isConnecting = False
        # maintains a LUT index by table containing a list of columns for it
        self._table_colums = {}

    def configure(self, context):
        super().configure(context)
        self.connect()

    def connect(self):
        self.isConnecting = True
        cnxn_string = (
            'DRIVER={};'
            'PORT={};'
            'SERVER={};'
            'DATABASE={};'
            'UID={};'
            'MARS_Connection={};'
            'PWD={}').format(
                '{ODBC Driver 17 for SQL Server}',
                self.connection().port(),
                self.connection().server(),
                self.connection().database(),
                self.connection().userid(),
                'yes' if self.connection().mars() else 'no',
                self.connection().password())
        self.logger.debug('Connecting: {}'.format(cnxn_string))
        self.cnxn = pyodbc.connect(cnxn_string)
        self.isConnecting = False

    def disconnect(self):
        if self.cnxn:
            self.cnxn.close()
            self.cnxn = None

    def stop(self):
        super().stop()
        self.disconnect()

    def validate_column(self, column, table, cursor):
        """ Makes sure column belongs to table

        Args:
            column (str): column in question
            table (str): table name
            cursor (pyodbc.Cursor): active cursor

        Returns:
            True/False
        """
        columns = self._table_colums.get(table)
        if columns is None:
            columns = [column.column_name for column in cursor.columns(table)]
            self._table_colums[table] = columns

        if column not in columns:
            cursor.close()
            raise ValueError(
                '\"{}\" is not a valid column in table \"{}\".'.format(
                    column, table))

        return column
