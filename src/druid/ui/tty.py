from prompt_toolkit.document import Document
from prompt_toolkit.widgets import TextArea


class TextAreaTTY:
    def __init__(self, textarea: TextArea):
        self.textarea = textarea

    def show(self, s):
        s = self.textarea.text + s.replace('\r', '')
        self.textarea.buffer.document = Document(
            text=s, 
            cursor_position=len(s),
        )
