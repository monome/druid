from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace


class CLICommand:

    def register(self, parser: ArgumentParser):
        parser.set_defaults(func=self)

    @abstractmethod
    def __call__(self, args: Namespace, config: dict):
        pass

    def help(self) -> str:
        return self.__doc__
