class DeviceNotFoundError(Exception):
    def __init__(self, msg, inner=None):
        super().__init__(msg)
        self.inner = inner
