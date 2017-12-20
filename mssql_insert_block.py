from nio.properties import VersionProperty, Property
from nio.signal.base import Signal
from .mssql_base_block import MSSQLBase

class MSSQLInsert(MSSQLBase):

    version = VersionProperty('0.1.0')
    query = Property(title='Query', default='INSERT INTO {{$table}} {{$columns}} VALUES {{$values}};')

    def process_signals(self, signals):
        output_signals = []
        cursor = self.cnxn.cursor()
        for signal in signals:
            result = cursor.execute(self.query(signal))
            output_signals.append(Signal({'inserted': result.rowcount}))
        self.notify_signals(output_signals)