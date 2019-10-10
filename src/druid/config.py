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

    info_file_handler:
      class: logging.handlers.RotatingFileHandler
      level: DEBUG
      formatter: simple
      filename: info.log
      maxBytes: 10485760 # 10MB
      backupCount: 20
      encoding: utf8

    error_file_handler:
      class: logging.handlers.RotatingFileHandler
      level: ERROR
      formatter: simple
      filename: errors.log
      maxBytes: 10485760 # 10MB
      backupCount: 20
      encoding: utf8

  loggers:
    my_module:
      level: ERROR
      handlers: [console]
      propagate: no

  root:
    level: DEBUG
    handlers: [console, info_file_handler, error_file_handler]

# logging:                      
#   version: 1
#   disable_existing_loggers: truee
#   formatters:
#     standard:
#       format: '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
#   handlers:
#     default:
#       level: DEBUG
#       class: logging.FileHandler
#       filename: druid.log
#       mode: w
#       formatter: standard
#   loggers:
#     '':
#       level: DEBUG
#       handlers: [default]
'''


class DruidConfig:
    def __init__(self, paths):
        self.config = anyconfig.loads(DEFAULT_DRUID_YML, ac_parser='yaml')
        anyconfig.merge(self.config, anyconfig.load(paths, ac_ignore_missing=True))

    def __getitem__(self, key):
        return self.config[key]
