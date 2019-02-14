from nio.properties import Property, VersionProperty, StringProperty
from nio.block.terminals import output
from .mssql_base import MSSQLBase
from nio.block.mixins.enrich.enrich_signals import EnrichSignals

@output('results', label='Results')
@output('no_results', label='No Results')
class MSSQLRawQuery(EnrichSignals, MSSQLBase):

    version = VersionProperty("1.0.0")
    query = StringProperty(
        title='Parameterized Query (use ? for any user-supplied values)',
        default='SELECT * FROM table where id=?',
        order=1)
    parameters = Property(
        title='Substitution Parameters (As List, In Order)',
        default='{{[]}}',
        order=2)

    def process_signals(self, signals, **kwargs):
        if self.is_connecting:
            self.logger.error('Connection already in progress. Dropping signals.')
            return

        cursor = self._get_cursor()

        output_signals = []

        for signal in signals:
            _query = self.query(signal)
            _parameters = self.parameters(signal)

            result = cursor.execute(_query, _parameters) if len(_parameters) > 0 else cursor.execute(_query)

            try:
                rows = result.fetchall()
                for row in rows:
                    hashed_row = zip([r[0] for r in cursor.description],row)
                    signal_dict = {a: b for a, b in hashed_row}
                    output_signals.append(self.get_output_signal(signal_dict, signal))

            except Exception:
                output_signals.append(self.get_output_signal({'inserted': result.rowcount}, signal))

        cursor.commit()
        cursor.close()

        if len(output_signals) > 0:
            self.notify_signals(output_signals, output_id='results')
        else:
            output_signals.append(self.get_output_signal({'results': 'null'}, signals[0]))
            self.notify_signals(output_signals, output_id='no_results')
