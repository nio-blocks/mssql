from nio.properties import Property, VersionProperty, StringProperty, ListProperty, PropertyHolder
from nio.block.terminals import output
from .mssql_base import MSSQLBase
from nio.block.mixins.enrich.enrich_signals import EnrichSignals

class ParamField(PropertyHolder):
    parameter = Property(
        default='{{ $param }}',
        title='Parameter',
        order=0,
        allow_none=True)

@output('results', label='Results')
@output('no_results', label='No Results')
class MSSQLRawQuery(EnrichSignals, MSSQLBase):

    version = VersionProperty("1.0.1")
    query = StringProperty(
        title='Parameterized Query (use ? for any user-supplied values)',
        default='SELECT * FROM table where id=?',
        order=1)
    params = ListProperty(
        ParamField,
        title='Substitution Parameters (In Order)',
        default=[],
        order=2)

    def process_signals(self, signals, **kwargs):
        if self.is_connecting:
            self.logger.error('Connection already in progress. Dropping signals.')
            return

        cursor = self._get_cursor()

        output_signals = []

        for signal in signals:
            _query = self.query()
            _params = list(param.parameter(signal) for param in self.params(signal))

            result = cursor.execute(_query, _params) if len(_params) > 0 else cursor.execute(_query)

            try:
                rows = result.fetchall()
                for row in rows:
                    hashed_row = zip([r[0] for r in cursor.description],row)
                    signal_dict = {a: b for a, b in hashed_row}
                    output_signals.append(self.get_output_signal(signal_dict, signal))

            except Exception:
                output_signals.append(self.get_output_signal({'affected_rows': result.rowcount}, signal))

        cursor.commit()
        cursor.close()

        if len(output_signals) > 0:
            self.notify_signals(output_signals, output_id='results')
        else:
            output_signals.append(self.get_output_signal({'results': None}, signals[0]))
            self.notify_signals(output_signals, output_id='no_results')
