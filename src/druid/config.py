import logging
import pprint

import anyconfig


logger = logging.getLogger(__name__)

DEFAULT_DRUID_YML = '''
sources:
  crow:
    - https://github.com/monome/crow
  druid:
    - https://github.com/monome/druid
  scripts:
    - https://github.com/monome/bowery

logging:
  version: 1
  disable_existing_loggers: False
  formatters:
    simple:
      format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

  handlers:
    console:
      class: logging.StreamHandler
      level: DEBUG
      formatter: simple
      stream: ext://sys.stdout

    file:
      class: logging.handlers.RotatingFileHandler
      level: DEBUG
      formatter: simple
      filename: logs/druid.log
      maxBytes: 10485760 # 10MB
      backupCount: 20
      encoding: utf8

    error_file:
      class: logging.handlers.RotatingFileHandler
      level: ERROR
      formatter: simple
      filename: logs/errors.log
      maxBytes: 10485760 # 10MB
      backupCount: 20
      encoding: utf8

  loggers:
    druid:
      level: DEBUG
      propagate: no

    root:
      level: DEBUG
      handlers: [console, file, error_file]
'''


class DruidConfig:
    def __init__(self, paths):
        self.config = anyconfig.loads(DEFAULT_DRUID_YML, ac_parser='yaml')
        anyconfig.merge(self.config, anyconfig.load(paths, ac_ignore_missing=True))

    def __getitem__(self, key):
        return self.config[key]
