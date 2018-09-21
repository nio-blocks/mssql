import pyodbc
from nio.block.base import Block
from nio.properties import (VersionProperty, StringProperty, PropertyHolder,
                            ObjectProperty, IntProperty, BoolProperty)
from nio.util.discovery import not_discoverable


class Credentials(PropertyHolder):

    userid = StringProperty(title='User ID', allow_none=True, order=1)
    password = StringProperty(title="Password", allow_none=True, order=2)


@not_discoverable
class MSSQLBase(Block):

    version = VersionProperty('0.1.0')
    server = StringProperty(title='Server', order=1)
    port = IntProperty(title='Port', default=1433, order=2)
    database = StringProperty(title='Database', order=3)
    credentials = ObjectProperty(Credentials, title='Connection Credentials',
                                 order=4)
    table = StringProperty(title='Table', default='{{ $table }}', order=5)
    mars = BoolProperty(title='Enable Multiple Active Result Sets',
                        default=False, order=6)

    def __init__(self):
        super().__init__()
        self.cnxn = None
        self.cursor = None
        self.isConnecting = False

    def configure(self, context):
        super().configure(context)
        self.connect()

    def connect(self):
        self.isConnecting = True
        cnxn_string = (
            'DRIVER={};'
            'PORT={};'
            'SERVER={};'
            'DATABASE={};'
            'UID={};'
            'MARS_Connection={};'
            'PWD={}').format(
                '{ODBC Driver 17 for SQL Server}',
                self.port(),
                self.server(),
                self.database(),
                self.credentials().userid(),
                'yes' if self.mars() else 'no',
                self.credentials().password())
        self.logger.debug('Connecting: {}'.format(cnxn_string))
        self.cnxn = pyodbc.connect(cnxn_string)
        self.isConnecting = False

    def disconnect(self):
        if self.cnxn:
            self.cnxn.close()

    def stop(self):
        super().stop()
        if self.cnxn:
            self.cnxn.close()
