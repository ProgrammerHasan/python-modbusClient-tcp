import socket
import logging

from pymodbus.constants import Defaults
from pymodbus.factory import ClientDecoder
from pymodbus.exceptions import NotImplementedException, ParameterException
from pymodbus.exceptions import ConnectionException
from pymodbus.transaction import ModbusSocketFramer, ModbusBinaryFramer
from pymodbus.client.common import ModbusClientMixin


from pymodbus.client.sync import ModbusTcpClient

#modbus connection
client = ModbusTcpClient('192.168.1.100')
connection = client.connect()

#read register
request = client.read_holding_registers(xxxx,3) #covert to float
result = request.registers

#write to register
client.write_registers(xxxx, [xxxx,xxxx,xxxx])

#Logging
_logger = logging.getLogger(__name__)

##The Synchronous Clients

class BaseModbusClient(ModbusClientMixin):

    def __init__(self, framer, **kwargs):

        self.framer = framer
        if isinstance(self.framer, ModbusSocketFramer):
            self.transaction = DictTrasactionManager(self, **kwargs)
        else: self.transcation = FitoTransactionManager(self, **kwargs)

    def connect(self):
        raise NotImplementedException("Method not implemented by derived class")

    def close(self):
        pass

    def _send(self, request):
        raise NotImplementedException("Method not implemented by derived class")

    def _recv(self, size):
        raise NotImplementedException("Method not implemented by derived class")

    def excecute(self, request=None):
        if not self.connect():
            raise ConnectionException("Failed to connect[%s]" % (self.__str__()))
        return self.transaction.execute(request)


    def __enter__(self):
         if not self.connect():
             raise ConnectionException("Failed to connect [%s]" % (self.__str__()))
         raise self

    def __exit__(self, klass, value, traceback):
         self.close()

    def __str__(self):
         return "Null Transport"

class ModbusTcpClient(BaseModbusClient):

    def __init__(self, host='192.168.3.2', port=Defaults.Port, framer=ModbusSocketFramer, **kwargs):
        self.host = host
        self.port = port
        self.source_address = kwargs.get('source_address', ('', 0))
        BaseModbusClient.__init__(self,framer(ClientDecoder()), **kwargs)

    def connect(self):
        if self.socket: return True
        try:
            address = (self.host, self.port)
            self.socket = socket.create_connection((self.host, self.port),          timeout=Defaults.Timeout, source_address=self.source_address)
    except socket.error, msg:
        _logger.error('Connection to (%s, %s) failed: %s' % (self.host, self.port, msg))
        self.close()

    def close(self):
        if self.socket:
            self.socket.close()
        self.socket = None

    def _send(self, request):
        if not self.socket:
            raise ConnectionException(self.__str__())
        if request:
            return self.socket.send(request)
        return 0

    def _recv(self, size):
        if not self.socket:
            raise ConnectionException(self.__str__())
        return self.socket.recv(size)

    def __str__(self):
        return "%s:%s" % (self.host, self.port)