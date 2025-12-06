import tkinter
import tkinter.font
from src.html.text import Text

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100


class Layout:
    def __init__(self, tokens):
        self.weight = "normal"
        self.style = "roman"
        self.size = 12
        self.display_list = []
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.display_list = []
        self.line = []

        for token in tokens:
            self.process_token(token)
        self.flush()


    def process_token(self, token):
        if isinstance(token, Text):
            for word in token.text.split():
                self.process_word(word)
        elif token.tag == "i":
            self.style = "italic"
        elif token.tag == "/i":
            self.style = "roman"
        elif token.tag == "b":
            self.weight = "bold"
        elif token.tag == "/b":
            self.weight = "normal"
        elif token.tag == "small":
            self.size -= 2
        elif token.tag == "/small":
            self.size += 2
        elif token.tag == "big":
            self.size += 4
        elif token.tag == "/big":
            self.size -= 4
        

    def process_word(self, word):
        font = tkinter.font.Font(size=self.size, weight=self.weight, slant=self.style)
        w = font.measure(word)
        # Newline support
        if w == "\n":
            self.cursor_x = HSTEP
            self.cursor_y += VSTEP
        self.display_list.append((self.cursor_x, self.cursor_y, word))
        self.cursor_x += w + font.measure(" ")
        if self.cursor_x + w > WIDTH - HSTEP:
            self.cursor_x = HSTEP
            self.cursor_y += font.metrics("linespace") * 1.25
            self.flush()
        self.line.append((self.cursor_x, word, font))
    
    def get_display_list(self):
        return self.display_list
    
    def flush(self):
        if not self.line:
            return
        metrices = [font.metrics() for x, word, font in self.line]
        max_ascent = max(m['ascent'] for m in metrices)
        baseline = self.cursor_y + 1.25 * max_ascent
        for x, word, font in self.line:
            y = baseline - font.metrics('ascent')
            self.display_list.append((x, y, word, font))
