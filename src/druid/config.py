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

scripts:
  default: sketch.lua

ui:
  style:
    'capture-field': '#747369'
    'output-field': '#d3d0c8'
    'input-field': '#f2f0ec'
    'line': '#747369'
  captures:
    - on_inputs: [1]
      stream: 'input[{args[0]}] = {args[1]}'
      change: 'input[{args[0]}] = {args[1]}'
    - on_inputs: [2]
      stream: 'input[{args[0]}] = {args[1]}'
      change: 'input[{args[0]}] = {args[1]}'
    - ii: '{line}'

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
      maxBytes: 65535
      backupCount: 2
      encoding: utf8

    error_file:
      class: logging.handlers.RotatingFileHandler
      level: ERROR
      formatter: simple
      filename: logs/errors.log
      maxBytes: 65535
      backupCount: 2
      encoding: utf8

  loggers:
    druid:
      level: INFO
      handlers: [file, error_file]

    root:
      level: DEBUG
      propagate: no
      handlers: [file, error_file]
'''


class DruidConfig:
    def __init__(self, paths):
        self.config = anyconfig.loads(DEFAULT_DRUID_YML, ac_parser='yaml')
        anyconfig.merge(self.config, anyconfig.load(paths, ac_ignore_missing=True))

    def __getitem__(self, key):
        return self.config[key]


class DruidConfigError(Exception):
    pass
