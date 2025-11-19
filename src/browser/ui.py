import os
import tkinter
import tkinter.font

from src.html.text import Text

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100

def layout(tokens: list) -> list[int, int, str]:
    weight = 'normal'
    style = 'roman'
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for token in tokens:
        if isinstance(token, Text):
            for word in token.text.split():
                font = tkinter.font.Font(
                    size=16,
                    weight=weight,
                    slant=style
                )
                w = font.measure(word)
                # Newline support
                if w == "\n":
                    cursor_x = HSTEP
                    cursor_y += VSTEP
                display_list.append((cursor_x, cursor_y, word))
                cursor_x += w + font.measure(" ")
                if cursor_x + w > WIDTH - HSTEP:
                    cursor_x = HSTEP
                    cursor_y += font.metrics("linespace") * 1.25
        elif token.tag == "i":
            style = "italic"
        elif token.tag == "/i":
            style = "roman"
        elif token.tag == "b":
            weight = "bold"
        elif token.tag == "/b":
            weight = "normal"

    return display_list

class BrowserUI:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)
        self.canvas.pack()
        self.scroll = 0

        self.set_title()
        self.set_scroll_event_callback()

    def set_scroll_event_callback(self):
        self.window.bind("<Down>", self.scrollDown)
        self.window.bind("<Up>", self.scrollUp)
        if os.name=="posix":
            self.window.bind("<Button-4>", self.scrollUp)
            self.window.bind("<Button-5>", self.scrollDown)

    def set_title(self):
        self.window.title("Bare Bone Browser")

    def clear_canvas(self):
        self.canvas.delete("all")

    def draw(self):
        self.clear_canvas()
        for x,y,c in self.display_list:
            if y > self.scroll + HEIGHT:
                continue
            # VSTEP has to be added to y because; y + VSTEP is the 
            # bottom edge of the character, because characters that are 
            # halfway inside the viewing window still have to be drawn
            if y +VSTEP < self.scroll:
                continue
            # anchor "nw" means the position (x,y) is the top-left corner of the text
            self.canvas.create_text(x, y - self.scroll, text=c, anchor="nw")

    def load(self, tokens: str):
        self.display_list = layout(tokens)
        self.draw()

    def scrollDown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

    def scrollUp(self, e):
        self.scroll -= SCROLL_STEP
        self.draw()
