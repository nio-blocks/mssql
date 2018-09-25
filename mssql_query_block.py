from nio.properties import VersionProperty
from nio.block.terminals import output
from .mssql_base import MSSQLBase
from .mssql_conditions import MSSQLConditions
from nio.block.mixins.enrich.enrich_signals import EnrichSignals


@output('results', label='Results')
@output('no_results', label='No Results')
class MSSQLQuery(EnrichSignals, MSSQLBase, MSSQLConditions):

    version = VersionProperty("0.2.0")

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

            output_signals = []
            for signal in signals:
                # determine query to execute
                table = self.table(signal)
                conditions, params = \
                    self.get_where_conditions(signal, table, cursor)
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
