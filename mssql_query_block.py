from enum import Enum
from nio.properties import ListProperty, Property, SelectProperty, \
                           StringProperty, VersionProperty, PropertyHolder
from nio import Signal
from nio.block.terminals import output
from .mssql_base import MSSQLBase
from nio.block.mixins.enrich.enrich_signals import EnrichSignals


class Operator(Enum):

    EQ = '='
    GT = '>'
    GTE = '>='
    LT = '<'
    LTE = '<='
    NOT = '!='
    NGT = '!>'
    NLT = '!<'

class Conditions(PropertyHolder):

    column = StringProperty(title='Column', order=20)
    operation = SelectProperty(Operator, title='Operator', order=21)
    value = Property(title='Value', order=22)

@output('results', label='Results')
@output('no_results', label='No Results')
class MSSQLQuery(EnrichSignals, MSSQLBase):

    version = VersionProperty('0.1.0')
    table = StringProperty(title='Table', default='{{ $table }}', order=10)
    conditions = ListProperty(Conditions,
                              title='Conditions',
                              deafult=[],
                              order=11)
    _query = 'SELECT * FROM {}'

    def process_signals(self, signals):
        if self.isConnecting:
            self.logger.error(
                'Connection already in progress. Dropping signals.')
        else:
            output_signals = []
            try:
                self.cursor = self.cnxn.cursor()
            except Exception as e:
                self.disconnect()
                self.connect()
                self.cursor = self.cnxn.cursor()
            for signal in signals:
                query, params = self._build_query(signal)
                self.logger.debug('Executing: {} with params {}'.format(
                    query, params))
                rows = self.cursor.execute(query, params).fetchall()
                self.logger.debug('Rows returned: {}'.format(len(rows)))
                for row in rows:
                    hashed_row = zip([r[0] for r in self.cursor.description],
                                     row)
                    signal_dict = {a: b for a, b in hashed_row}
                    output_signals.append(
                        self.get_output_signal(signal_dict, signal))
            self.cursor.close()

            if len(output_signals) > 0:
                self.notify_signals(output_signals, output_id='results')
            else:
                output_signals.append(self.get_output_signal(
                    {'results': 'null'}, signals[0]))
                self.notify_signals(output_signals, output_id='no_results')

    def _build_query(self, signal):
        table = self.table(signal)
        query = self._query.format(table)
        params = []
        for i, condition in enumerate(self.conditions()):
            if i == 0:
                query += ' WHERE '
            else:
                query += ' AND '
            condition_string = '{} {} ?'.format(
                self._validate_column(condition.column(signal), table),
                condition.operation(signal).value)
            query += condition_string
            params.append(condition.value(signal))
        return query, params

    def _validate_column(self, target_column, target_table):
        """ Raises ValueError if column is not valid in the target table"""
        valid_columns = []
        for column in self.cursor.columns(target_table):
            valid_columns.append(column.column_name)
        if target_column not in valid_columns:
            self.cursor.close()
            raise ValueError(
                '\"{}\" is not a valid column in table \"{}\".'.format(
                    target_column, target_table))
        return target_column
