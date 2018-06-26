import pyodbc
from nio.block.base import Block
from nio.properties import (VersionProperty, StringProperty, PropertyHolder,
                            ObjectProperty, IntProperty, BoolProperty)
from nio.signal.base import Signal
from nio.util.discovery import not_discoverable

driver_name = ''

try:
  driver_names = [x for x in pyodbc.drivers() if x.endswith(' for SQL Server')]
  if driver_names:
      driver_name = driver_names[0]
  if not driver_name:
      raise ReferenceError('No suitable ODBC driver found. Block will not be able to connect to MSSQL DB. View README.md to install driver.')
except ReferenceError as error:
  print(error)


class Credentials(PropertyHolder):

    userid = StringProperty(title='User ID', allow_none=True)
    password = StringProperty(title="Password", allow_none=True)

@not_discoverable
class MSSQLBase(Block):

    version = VersionProperty('0.1.0')
    server = StringProperty(title='Server')
    port = IntProperty(title='Port')
    database = StringProperty(title='Database')
    credentials = ObjectProperty(Credentials, title='Connection Credentials')
    mars = BoolProperty(title='Enable Multiple Active Result Sets', default=False)

    def __init__(self):
        super().__init__()
        self.cnxn = None
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
                driver_name,
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
        self.cnxn.close()

    def stop(self):
        super().stop()
        self.cnxn.close()
