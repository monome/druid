import asyncio
import logging

from serial_asyncio import create_serial_connection
import serial
import serial.tools.list_ports

from druid.io.device import DeviceNotFoundError


logger = logging.getLogger(__name__)


class SerialDevice:

    @classmethod
    def find(cls, hwid, **kwargs):
        for portinfo in serial.tools.list_ports.comports():
            logger.info(
                "comport {} - device {} - {}".format(
                    portinfo.device,
                    portinfo.hwid,
                    portinfo.description,
                ),
            )
            if hwid in portinfo.hwid:
                logger.info("using {}".format(portinfo.device))
                try:
                    return cls(portinfo, **kwargs)
                except serial.SerialException as exc:
                    logger.info(
                        'error connecting to {}:\n{}'.format(
                            portinfo.device,
                            exc,
                        ),
                    )
                    raise DeviceNotFoundError("error connecting to device {}".format(hwid))
        raise DeviceNotFoundError("can't find device {}".format(hwid))

    def __init__(self, port, baudrate=115200, timeout=0.1):
        self.port = port
        self.serial = serial.Serial(
            port.device, 
            baudrate=baudrate, 
            timeout=timeout,
        )
        
    def write(self, b):
        logger.debug('-> device {}: {}'.format(self.port.device, b))
        logger.debug('serial port: {}'.format(self.serial))
        self.serial.write(b)

    def read(self, *args, **kwargs):
        b = self.serial.read(*args, **kwargs)
        if len(b) > 0:
            logger.debug('<- device {}: {}'.format(self.port.device, b))
        return b


class SerialProtocolBase(asyncio.Protocol):
    def __init__(self, handlers=None):
        self.handlers = {
            'connect': lambda r: None,
            'disconnect': lambda r, exc: None,
            'data': lambda r, s: None,
        }
        if handlers is not None:
            self.handlers.update(handlers)

    def connection_made(self, transport):
        self.transport = transport
        self.notify('connect', self)
        logger.debug('transport connected: {}'.format(self.transport))

    def connection_lost(self, exc):
        logger.debug('connection lost: {}\n{}'.format(self.transport, exc))
        self.notify('disconnect', self, exc)
    
    def notify(self, msg, *args):
        try:
            handler = self.handlers[msg]
        except KeyError:
            logger.debug('unknown message: {}'.format(msg))
        else:
            if hasattr(handler, '__call__'):
                handler(msg, *args)
            elif isinstance(handler, list):
                for sub in handler:
                    if hasattr(sub, '__call__'):
                        sub(msg, *args)


class SerialReaderProtocol(asyncio.StreamReaderProtocol):
    def __init__(self, reader, loop, handlers=None):
        super().__init__(reader, loop)        
        self.handlers = {
            'connect': lambda evt, p, t: None,
            'disconnect': lambda evt, p, exc: None,
            # 'data': lambda r, s: None,
        }
        if handlers is not None:
            self.handlers.update(handlers)


    def notify(self, msg, *args):
        try:
            handler = self.handlers[msg]
        except KeyError:
            logger.debug('unknown message: {}'.format(msg))
        else:
            if hasattr(handler, '__call__'):
                handler(msg, *args)
            elif isinstance(handler, list):
                for sub in handler:
                    if hasattr(sub, '__call__'):
                        sub(msg, *args)


    def connection_made(self, transport):
        # super().connection_made(transport)
        logger.debug('connection made: {}'.format(transport))
        self.notify('connect', self, transport)

    def connection_lost(self, exc):
        logger.debug('connection lost: {}'.format(exc))
        self.notify('disconnect', self, exc)
        # super().connection_lost(exc)

    # def data_received(self, data):
    #     self.buf += data
    #     if self.terminator in self.buf:
    #         packets = self.buf.split(self.terminator)
    #         self.buf = packets[-1]
    #         for packet in packets[:-1]:
    #             self.notify('data', self, packet)


class AsyncSerialDevice(SerialDevice):
    
    def __init__(self, port, terminator=b'\n\r', **kwargs):
                 # port, baudrate=115200, timeout=0.1,
                 # terminator=b'\n\r',
                 # loop=None, handlers=None):
        # super().__init__(
        #     port, 
        #     baudrate=baudrate,
        #     timeout=timeout,
        #     handlers=handlers,
        # )
        self.port = port
        self.kwargs = kwargs
        self.terminator = terminator
        # self.reader, self.writer = self.open_serial_connection(
        #     port.device,
        #     baudrate=baudrate,
        #     timeout=timeout,
        #     handlers=handlers,
        #     loop=loop,
        # )

    @asyncio.coroutine
    def open_serial_connection(self, 
                               port, 
                               loop=None, limit=asyncio.streams._DEFAULT_LIMIT,
                               handlers=None, 
                               **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader(limit=limit, loop=loop)
        protocol = SerialReaderProtocol(
            reader, 
            loop=loop,
            handlers=handlers,
        )
        transport, _ = yield from create_serial_connection(
            url=port.device,
            loop=loop,
            protocol_factory=lambda: protocol,
            **kwargs,
        )
        writer = asyncio.StreamWriter(transport, protocol, reader, loop)
        return (reader, writer)

    async def listen(self, parser):
        while True:
            logger.debug('attempting to connect to port: {}'.format(self.port))
            self.reader, self.writer = await self.open_serial_connection(self.port, **self.kwargs)
            async for packet in self.recv(self.reader):
                parser.parse(packet)

    def write(self, b):
        # b = bytes(s, encoding)
        logger.debug('-> device {}: {}'.format(self.port.device, b))
        self.writer.write(b)

    async def recv(self, reader):
        while True:
            try:
                b = await reader.readuntil(self.terminator)
                logger.debug('<- device {}: {}'.format(self.port.device, b))
                yield b
            except Exception as e:
                logger.debug('error during read: {}'.format(e))
                return


    #     loop = asyncio.get_event_loop()
    #     self.port = port
    #     self.reader = create_serial_connection(
    #         loop, 
    #         lambda: SerialReader(handlers=handlers), 
    #         baudrate=baudrate,
    #         timeout=timeout,
    #     )
    #     self.writer = create_serial_connection(
    #         loop,
    #         lambda: SerialWriter(handlers=handlers),
    #         baudrate=baudrate,
    #         timeout=timeout,
    #     )
        
    # def run(self):
    #     return asyncio.gather(self.reader, self.writer)

    # async def 
