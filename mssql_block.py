from nio.block.base import Block
from nio.properties import VersionProperty, StringProperty, PropertyHolder, ObjectProperty, Property
from nio.signal.base import Signal
import pyodbc

class Credentials(PropertyHolder):

    userid = StringProperty(title='User ID', allow_none=True)
    password = StringProperty(title="Password", allow_none=True)

class MSSQL(Block):

    version = VersionProperty('0.1.0')
    server = StringProperty(title='Server')
    database = StringProperty(title='Database')
    credentials = ObjectProperty(Credentials, title='Connection Credentials')
    query = Property(title='Query', default='SELECT * from {{ $table }}')

    def __init__(self):
        super().__init__()
        self.cnxn = None

    def configure(self, context):
        super().configure(context)
        cnxn_string = (
            'DRIVER={};'
            'SERVER={};'
            'DATABASE={};'
            'UID={};'
            'PWD={}').format(
                '{ODBC Driver 13 for SQL Server}',
                self.server(),
                self.database(),
                self.credentials().userid(),
                self.credentials().password())
        raw_cnxn_string = '%r'%cnxn_string  # cast to raw string literal
        self.cnxn = pyodbc.connect(raw_cnxn_string[1:-1]) # strip extra quotes apparently

    def process_signals(self, signals):
        output_signals = []
        cursor = self.cnxn.cursor()
        for signal in signals:
            rows = cursor.execute(self.query(signal)).fetchall()
            for row in rows:
                signal_dict = {key: getattr(row, key) for key in dir(row) if not key.startswith('__')}
                output_signals.append(Signal(signal_dict))
        self.notify_signals(output_signals)

    def stop(self):
        super().stop()
        self.cnxn.close()
