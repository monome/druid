import logging
import time

from druid.io.device import DeviceNotFoundError
from druid.io.serial.device import SerialDevice


logger = logging.getLogger(__name__)


class Crow:
    DEVICE_ID = "USB VID:PID=0483:5740"

    def connect(self, on_connect=None):
        try:
            self.serial = SerialDevice.find(self.DEVICE_ID)
        except DeviceNotFoundError:
            raise DeviceNotFoundError("crow device not found")
        else:
            if on_connect is not None:
                on_connect(self.serial)

    def close(self):
        self.serial.close()

    def read(self, count):
        buf = self.serial.read(count)
        logger.debug('read: {}'.format(repr(buf)))
        return buf

    def write(self, s):
        try:
            self.serial.write(s)
        except Exception as exc:
            logger.error(exc)
            self.connect()

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
        time.sleep(0.2)  # wait for allocation
        tty.show(' file uploaded: {}'.format(script_file))
        self.writefile(script_file)
        time.sleep(0.2)  # wait for upload to complete
        self.write(cmd)

    def upload(self, tty, script_file):
        tty.show(' uploading {}\n\r'.format(script_file))
        self.script(tty, script_file, '^^w')

    def execute(self, tty, script_file):
        tty.show(' running {}\n\r'.format(script_file))
        self.script(tty, script_file, '^^e')

    def dump(self):
        self.writeline("^^p")
        return self.read(1000000).decode()

        

class CrowParser:
    def __init__(self, tty, event_handlers):
        self.tty = tty
        self.event_handlers = event_handlers


    def parse(self, s):
        lines = s.decode('ascii').split('\n\r')
        for line in lines:
            self.parse_line(line)

    def parse_line(self, line):
        if "^^" in line:
            cmds = line.split('^^')
            for cmd in cmds:
                t3 = cmd.rstrip().partition('(')
                if len(t3) != 3:
                    continue
                x = t3[0]
                args = t3[2].rstrip(')').partition(',')

                curr = self.event_handlers
                for cmp in evt.split('.'):
                    try:
                        curr = curr[cmp]
                    except KeyError:
                        break
                    else:
                        if hasattr(curr, '__call__'):
                            return curr(line, evt, args)
        elif len(line) > 0:
            self.tty.show(line + '\n')
