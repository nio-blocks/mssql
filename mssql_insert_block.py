from nio.properties import VersionProperty, StringProperty, Property
from nio.signal.base import Signal
from .mssql_base_block import MSSQLBase

class MSSQLInsert(MSSQLBase):

    version = VersionProperty('0.1.0')
    row = Property(title='Row', default='{{ $.to_dict() }}')
    table = StringProperty(title='Target Table', default='')

    def process_signals(self, signals):
        cursor = self.cnxn.cursor()
        inserted = 0
        for signal in signals:
            row_dict = self.row(signal)
            cols = ''
            vals = ''
            for key in row_dict:
                cols += key + ', '
                val = row_dict[key]
                if isinstance(val, str):
                    # double-up quote chars to escape without backslash hell
                    val = val.replace('\'', '\'\'').replace('\"', '\"\"')
                    val = '\'' + val + '\''
                vals += str(val) + ', '
            query = 'INSERT INTO {} ({}) VALUES ({});'.format(
                self.table(signal),
                cols[:-2],
                vals[:-2])
            self.logger.debug(cols[:-2])
            self.logger.debug(vals[:-2])
            self.logger.debug(query)
            result = cursor.execute(query)
            inserted += result.rowcount
        cursor.commit()
        self.notify_signals(Signal({'inserted': inserted}))
