from nio.properties import (StringProperty)
from nio.util.discovery import not_discoverable

from .mssql_base import MSSQLBase


@not_discoverable
class MSSQLTabledBase(MSSQLBase):
    table = StringProperty(title='Table', default='TableName', order=1)

    def __init__(self):
        super().__init__()
        # maintains a LUT index by table containing a list of columns for it
        self._table_lut = {}

    def validate_column(self, column, table, cursor):
        """ Makes sure column belongs to table

        Args:
            column (str): column in question
            table (str): table name
            cursor (pyodbc.Cursor): active cursor

        Returns:
            True/False
        """
        columns = self._table_lut.get(table)
        if columns is None:
            columns = tuple(column.column_name for column in cursor.columns(table))
            self._table_lut[table] = columns

        if column not in columns:
            cursor.close()
            raise ValueError(
                '\"{}\" is not a valid column in table \"{}\".'.format(
                    column, table))

        return column
