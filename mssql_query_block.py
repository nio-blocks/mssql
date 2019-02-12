from nio.properties import Property, VersionProperty, ListProperty, StringProperty, PropertyHolder
from nio.block.terminals import output
from .mssql_base import MSSQLBase
from nio.block.mixins.enrich.enrich_signals import EnrichSignals

class Parameter(PropertyHolder):
    param = Property(title='Parameter')

@output('results', label='Results')
@output('no_results', label='No Results')
class MSSQLQuery(EnrichSignals, MSSQLBase):

    version = VersionProperty("1.0.0")
    query = StringProperty(title='Parameterized Query (use ? for any user-supplied values)', default='SELECT * FROM table where id=?', order=10)
    parameters = ListProperty(Parameter, title='Substitution Parameter (In Order)', default=[], order=11)

    def process_signals(self, signals):
        if self.isConnecting:
            self.logger.error('Connection already in progress. Dropping signals.')
        else:
            try:
                cursor = self.cnxn.cursor()
            except Exception as e:
                self.disconnect()
                self.connect()
                cursor = self.cnxn.cursor()

            output_signals = []

            for signal in signals:
                _query = self.query(signal)
                _parameters = tuple(p.param(signal) for p in self.parameters())

                rows = cursor.execute(_query, _parameters).fetchall()

                for row in rows:
                    hashed_row = zip([r[0] for r in cursor.description], row)
                    signal_dict = {a: b for a, b in hashed_row}
                    output_signals.append(self.get_output_signal(signal_dict, signal))

            cursor.close()

            if len(output_signals) > 0:
                self.notify_signals(output_signals, output_id='results')
            else:
                output_signals.append(self.get_output_signal({'results': 'null'}, signals[0]))
                self.notify_signals(output_signals, output_id='no_results')
