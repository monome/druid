from prompt_toolkit.document import Document
from prompt_toolkit.widgets import TextArea


class FuncTTY:
    def __init__(self, show_func):
        self.show_func = show_func

    def show(self, s):
        self.show_func(s)


class TextAreaTTY:
    def __init__(self, textarea: TextArea):
        self.textarea = textarea

    def show(self, s, fmt=lambda s: s):
        s = self.textarea.text + fmt(s.replace('\r', ''))
        self.textarea.buffer.document = Document(
            text=s,
            cursor_position=len(s),
        )
