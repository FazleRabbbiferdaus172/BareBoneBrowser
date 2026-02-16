import tkinter
import tkinter.font
from src.html.text import Text
from src.cache.font_cache import FontCache

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
        self.font_cache = FontCache()

        for token in tokens:
            self.process_token(token)
        # Todo: Fix flush or make support for font
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
        elif token.tag == "br":
            self.flush()
        elif token.tag == "/p":
            self.flush()
            self.cursor_y += VSTEP
        

    def process_word(self, word):
        font = self.font_cache.get(size=self.size, weight=self.weight, style=self.style)
        w = font.measure(word)
        ending_space = font.measure(" ")

        # Newline support
        if w == "\n":
            self.cursor_x = HSTEP
            self.cursor_y += VSTEP
        self.line.append((self.cursor_x, word, font))
        self.cursor_x += w + ending_space
        if self.cursor_x + w > WIDTH - HSTEP:
            self.cursor_x = HSTEP
            self.cursor_y += font.metrics("linespace") * 1.25
            self.flush()
    
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
        max_descent = max(metric["descent"] for metric in metrices)
        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = HSTEP
        self.line = []
