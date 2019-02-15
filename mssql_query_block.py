from nio.properties import VersionProperty, StringProperty
from nio.block.terminals import output
from nio.block.mixins.enrich.enrich_signals import EnrichSignals

from .mssql_base import MSSQLTabledBase
from .mssql_conditions import MSSQLConditions


@output('results', label='Results')
@output('no_results', label='No Results')
class MSSQLQuery(EnrichSignals, MSSQLTabledBase, MSSQLConditions):

    version = VersionProperty("1.0.1")

    def process_signals(self, signals, **kwargs):
        if self.is_connecting:
            self.logger.error('Connection already in progress. Dropping signals.')
            return

        cursor = self._get_cursor()

        output_signals = []
        for signal in signals:
            # determine query to execute
            table = self.table()
            conditions, params = \
                self._get_where_conditions(signal, table, cursor)
            query = 'SELECT * FROM {}'.format(table) + conditions
            self.logger.debug('Executing: {} with params {}'.format(
                query, params))

            rows = cursor.execute(query, params).fetchall()
            self.logger.debug('{} rows returned for signal: {}'.
                              format(len(rows), signal.to_dict()))
            for row in rows:
                hashed_row = zip([r[0] for r in cursor.description],
                                 row)
                signal_dict = {a: b for a, b in hashed_row}
                output_signals.append(
                    self.get_output_signal(signal_dict, signal))

        cursor.close()

        if len(output_signals) > 0:
            self.notify_signals(output_signals, output_id='results')
        else:
            output_signals.append(self.get_output_signal(
                {'results': 'null'}, signals[0]))
            self.notify_signals(output_signals, output_id='no_results')
