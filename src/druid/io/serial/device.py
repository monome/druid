import asyncio
import logging
import os

from serial_asyncio import SerialTransport
import serial
import serial.tools.list_ports
import traceback

from druid.io.device import DeviceNotFoundError


logger = logging.getLogger(__name__)

# some tweaks to serial_asyncio to get it working on Windows
class SerialDeviceTransport(SerialTransport):
    if os.name == "nt":
        def _poll_read(self):
            if self._has_reader:
                try:
                    waiting = self.serial.in_waiting
                except serial.SerialException as exc:
                    self._fatal_error(exc)
                else:
                    if waiting:
                        self._loop.call_soon(self._read_ready)
                self._loop.call_later(self._poll_wait_time, self._poll_read)

        def _poll_write(self):
            if self._has_writer:
                try:
                    waiting = self.serial.out_waiting
                except serial.SerialException as exc:
                    self._fatal_error(exc)
                else:
                    if waiting:
                        self._loop.call_soon(self._write_ready)
                self._loop.call_later(self._poll_wait_time, self._poll_write)

    def _call_connection_lost(self, exc):
        """Close the connection.

        Informs the protocol through connection_lost() and clears
        pending buffers and closes the serial connection.
        """
        assert self._closing
        assert not self._has_writer
        assert not self._has_reader
        if os.name == "nt":
            try:
                self._serial.flush()
            except serial.SerialException as flush_exc:
                logger.info('unable to flush serial port: {}'.format(flush_exc))
        else:
            try:
                self._serial.flush()
            except termios.error:
                # ignore termios errors which may happen if the serial device was
                # hot-unplugged.
                pass
        try:
            self._protocol.connection_lost(exc)
        finally:
            self._write_buffer.clear()
            self._serial.close()
            self._serial = None
            self._protocol = None
            self._loop = None


    def _fatal_error(self, exc, message='Fatal error on serial transport'):
        logger.debug('fatal transport error: {}'.format(exc))
        self._abort(exc)
        raise

@asyncio.coroutine
def create_serial_connection(loop, protocol_factory, *args, **kwargs):
    ser = serial.serial_for_url(*args, **kwargs)
    logger.debug('serial port: {}'.format(ser))
    protocol = protocol_factory()
    transport = SerialDeviceTransport(loop, protocol, ser)
    return (transport, protocol)

@asyncio.coroutine
def open_serial_connection(port,
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
    logger.debug('creating connection: {}'.format(port))
    transport, _ = yield from create_serial_connection(
        url=port,
        loop=loop,
        protocol_factory=lambda: protocol,
        **kwargs,
    )
    writer = asyncio.StreamWriter(transport, protocol, reader, loop)
    return (reader, writer)


def find_serial_device(hwid):
    logger.debug('scan for device {}'.format(hwid))
    for portinfo in serial.tools.list_ports.comports():
        logger.info(
            'comport {} - device {} - {}'.format(
                portinfo.device,
                portinfo.hwid,
                portinfo.description,
            ),
        )
        if hwid in portinfo.hwid:
            logger.info('found {}'.format(hwid))
            return portinfo
    raise DeviceNotFoundError("can't find device {}".format(hwid))

class SerialDevice:

    @classmethod
    def find(cls, hwid, **kwargs):
        portinfo = find_serial_device(hwid)
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
        logger.info('connection made: {}'.format(transport.serial.port))
        self.notify('connect', self, transport)

    def connection_lost(self, exc):
        logger.debug('connection lost: {}'.format(exc))
        self.notify('disconnect', self, exc)
        super().connection_lost(exc)


class AsyncSerialDevice:
    
    def __init__(self,
                 device_id,
                 terminator=b'\n\r', handlers=None,
                 **kwargs):
        self.device_id = device_id
        self.serial_kwargs = dict(baudrate=115200, timeout=0.1)
        self.terminator = terminator
        self.handlers = handlers
        self._writeq = asyncio.Queue()

    async def listen(self, parser):
        while True:
            try:
                portinfo = find_serial_device(self.device_id)
                reader, writer = await open_serial_connection(
                    portinfo.device,
                    handlers=self.handlers,
                    **self.serial_kwargs,
                )
            except Exception as exc:
                logger.debug('couldnt connect: {}'.format(traceback.format_exc()))
                await asyncio.sleep(1.0)
            else:
                try:
                    results = await asyncio.gather(
                        self.send(portinfo, writer),
                        self.recv(portinfo, reader, parser),
                        return_exceptions=True
                    )
                    logger.debug('gather results: {}'.format(results))
                except Exception as e:
                    logger.debug('errored during send/recv: {}'.format(e))
                finally:
                    await asyncio.sleep(1.0)
                

    def write(self, b):
        self._writeq.put_nowait(b)

    async def send(self, portinfo, writer):
        while True:
            b = await self._writeq.get()
            logger.debug('-> device {}: {}'.format(portinfo.device, b))
            try:
                writer.write(b)
                await writer.drain()
            except Exception as e:
                logger.info('error during write: {}'.format(e))
                break

    async def recv(self, portinfo, reader, parser):
        while True:
            try:
                logger.debug('waiting for read')
                b = await reader.readline()
                logger.debug('<- device {}: {}'.format(portinfo.device, b))
                if len(b) > 0:
                    logger.debug('handing to parser')
                    parser.parse(b)
            except Exception as e:
                logger.info('error during read: {}'.format(e))
                break
