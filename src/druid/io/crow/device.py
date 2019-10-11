import logging


logger = logging.getLogger(__name__)


class Crow:
    def __enter__(self):
        return self

    def __exit__(self, type, exc, traceback):
        logger.info('crow disconnecting:', exc)

    def write(self, s):
        pass

    def cmd(self, c):
        pass

    def execute(self, tty, script_file):
        pass

    def upload(self, tty, script_file):
        pass
