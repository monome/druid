from argparse import Action, ArgumentError
import os


class DirectoryArgumentAction(Action):
    
    def __call__(self,
                 parser, namespace, values,
                 option_string=None):
        path = os.path.realpath(values)
        if not os.path.isdir(path):
            raise ArgumentError(self, 'could not find config directory "{}"'.format(path))
        if not os.access(path, os.R_OK):
            raise ArgumentError(self, 'could not read config directory "{}"'.format(path))
        setattr(namespace, self.dest, path)
