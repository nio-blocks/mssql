from .mssql_column import validate_column
from nio.properties import VersionProperty, StringProperty, PropertyHolder, \
    Property, ListProperty
from nio.signal.base import Signal
from .mssql_base import MSSQLBase
from .mssql_conditions import MSSQLConditions


class ColumnValue(PropertyHolder):

    column = StringProperty(title='Column', order=20)
    value = Property(title='Value', order=21)


class MSSQLUpdate(MSSQLBase, MSSQLConditions):

    version = VersionProperty('0.1.0')
    column_values = ListProperty(ColumnValue,
                                 title='Column Values',
                                 deafult=[],
                                 order=11)

    def process_signals(self, signals):
        if self.isConnecting:
            self.logger.error(
                'Connection already in progress. Dropping signals.')
        else:
            try:
                cursor = self.cnxn.cursor()
            except Exception as e:
                self.disconnect()
                self.connect()
                cursor = self.cnxn.cursor()

            total_rows = 0
            for signal in signals:
                # determine query to execute
                table = self.table(signal)
                column_values, params = \
                    self._get_column_values(signal, table, cursor)
                conditions, where_params = \
                    self.get_where_conditions(signal, table, cursor)
                params.extend(where_params)
                update = \
                    'UPDATE {} SET {}'.format(table, column_values) + conditions
                self.logger.debug('Executing: {} with params {}'.format(
                    update, params))

                row_count = cursor.execute(update, params).rowcount
                self.logger.debug('{} rows returned for signal: {}'.
                                  format(row_count, signal.to_dict()))
                total_rows += row_count

            self.logger.debug('Rows updated: {}'.format(total_rows))

            cursor.commit()
            cursor.close()

            self.notify_signals([Signal({'Rows updated': total_rows})])

    def _get_column_values(self, signal, table, cursor):

        column_values = ""
        params = []
        for i, column_value in enumerate(self.column_values()):
            if i != 0:
                column_values += ', '
            condition_string = '{} = ?'.format(
                validate_column(column_value.column(signal), table, cursor))
            params.append(column_value.value(signal))
            column_values += condition_string

        return column_values, params
