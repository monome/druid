## Developing Druid

You may wish to set up a virtualenv to avoid conflicts with other
Python packages on your system:

```
python3 -m venv .venv
source .venv/bin/activate  # this may be different depending on your platform / shell
                     # may also be Scripts/activate.*
python setup.py develop
```

After running `python setup.py develop`, you should be able to run
`druid` as you make changes without running anything else. You can
`tail -f logs/druid.log` while druid is running to get logs from the
standard Python `logging` library. Write to this log via

```
import logging

logger = logging.getLogger(__name__)
logger.debug('hi')
```
