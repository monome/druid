from abc import ABC, abstractmethod
import asyncio
import logging
import time

from druid.io.device import DeviceNotFoundError
from druid.io.serial.device import (
    find_serial_device,
    AsyncSerialDevice,
    SerialDevice,
)
from druid.ui.tty import FuncTTY


logger = logging.getLogger(__name__)


class CrowBase(ABC):
    DEVICE_ID = "USB VID:PID=0483:5740"

    @classmethod
    def find_device(cls):
        try:
            find_serial_device(cls.DEVICE_ID)
        except DeviceNotFoundError:
            raise DeviceNotFoundError('crow not found')

    def __init__(self, tty=None):
        if tty is None:
            tty = FuncTTY(lambda s: None)
        self.tty = tty

    def attach(self, tty):
        self.tty = tty

    @abstractmethod
    def connect(self, handlers=None):
        pass

    @abstractmethod
    def write(self, s):
        pass

    def writeline(self, s):
        self.write(s + '\r\n')

    def writefile(self, f):
        with open(f) as d:
            lua = d.readlines()
            for line in lua:
                self.write(line)
                time.sleep(0.002)  # fix os x crash?

    def script(self, tty, script_file, cmd):
        self.write('^^s'),
        time.sleep(0.5)  # wait for allocation
        tty.show(' file uploaded: {}'.format(script_file))
        self.writefile(script_file)
        time.sleep(0.5)  # wait for upload to complete
        self.write(cmd)

    def upload(self, tty, script_file):
        tty.show(' uploading {}\n\r'.format(script_file))
        self.script(tty, script_file, '^^w')

    def execute(self, tty, script_file):
        tty.show(' running {}\n\r'.format(script_file))
        self.script(tty, script_file, '^^e')

    @abstractmethod
    async def listen(self, parser):
        pass

class Crow(CrowBase):

    def connect(self):
        try:
            self.serial = SerialDevice.find(self.DEVICE_ID)
        except DeviceNotFoundError:
            raise DeviceNotFoundError("crow device not found")

    def close(self):
        self.serial.close()

    def read(self, count):
        return self.serial.read(count)

    def write(self, s):
        self.serial.write(bytes(s, 'utf-8'))

    def dump(self):
        self.writeline("^^p")
        return self.read(1000000).decode()

    async def listen(self, parser):
        while True:
            sleeptime = 0.001
            try:
                r = self.read(10000)
            except Exception as exc:
                logger.debug('error during read: {}'.format(exc))
                self.tty.show(' <lost connection>')
                sleeptime = 1.0
                logger.info('lost connection: {}'.format(exc))
                self.connect()
            else:
                if len(r) > 0:
                    parser.parse(r)
            await asyncio.sleep(sleeptime)
        

class CrowAsync(CrowBase):

    def __init__(self):
        self.serial = AsyncSerialDevice(
            self.DEVICE_ID,
            handlers={
                'connect': self.on_connect,
                'disconnect': self.on_disconnect,
            },
        )

    def connect(self):
        try:
            self.find_device(self.DEVICE_ID)
        except DeviceNotFoundError:
            raise DeviceNotFoundError('crow device not found')

    def on_connect(self, evt, protocol, transport):
        self.tty.show(' <connected>\r\n')

    def on_disconnect(self, evt, protocol, transport):
        self.tty.show(' <connection lost>\r\n')

    def write(self, s):
        self.serial.write(bytes(s, 'utf-8'))

    async def listen(self, parser):
        await self.serial.listen(parser)

    def writeline(self, s):
        self.write(s + '\r\n')

    def writefile(self, f):
        with open(f) as d:
            lua = d.readlines()
            for line in lua:
                self.write(line)
                time.sleep(0.002)

    def script(self, tty, script_file, cmd):
        self.write('^^s'),
        time.sleep(0.2)  # wait for allocation
        tty.show(' file uploaded: {}'.format(script_file))
        self.writefile(script_file)
        time.sleep(0.2)  # wait for upload to complete
        self.write(cmd)

    def upload(self, tty, script_file):
        tty.show(' uploading {}\n\r'.format(script_file))
        self.script(tty, script_file, '^^w')



class CrowParser:
    def __init__(self, tty, event_handlers):
        self.tty = tty
        self.event_handlers = event_handlers


    def parse(self, s):
        lines = s.decode('ascii').splitlines()
        for line in lines:
            line = line.strip()
            if len(line) > 0:
                self.parse_line(line)

    def parse_line(self, line):
        if "^^" in line:
            cmds = line.split('^^')
            for cmd in cmds:
                t3 = cmd.rstrip().partition('(')
                if not any(t3):
                    continue
                evt = t3[0]
                args = t3[2].rstrip(')').split(',')

                logger.debug('crow event: {}'.format(line))
                self.handle_event(line, evt, args)
        elif len(line) > 0:
            self.tty.show(line + '\n')

    def handle_event(self, line, evt, args):
        curr = self.event_handlers
        for cmp in evt.split('.'):
            try:
                curr = curr[cmp]
            except KeyError:
                break
            else:
                if hasattr(curr, '__call__'):
                    logger.debug('found handler: {} {}'.format(evt, curr))
                    return curr(line, evt, args)
                if isinstance(curr, list):
                    try:
                        ch = int(args[0])
                    except ValueError:
                        pass
                    else:
                        if len(args) > 0 and 1 <= ch <= len(curr):
                            if hasattr(curr[ch - 1], '__call__'):
                                logger.debug('found handler: {} {}'.format(evt, curr[ch - 1]))
                                return curr[ch - 1](line, evt, args)
        self.tty.show(line)
