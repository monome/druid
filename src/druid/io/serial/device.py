import logging

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
        
    def write(self, s, encoding='utf-8'):
        b = bytes(s, encoding)
        logger.debug('-> device {}: {}'.format(self.port.device, b))
        self.serial.write(b)

    def read(self, *args, **kwargs):
        b = self.serial.read(*args, **kwargs)
        if len(b) > 0:
            logger.debug('<- device {}: {}'.format(self.port.device, b))
        return b
