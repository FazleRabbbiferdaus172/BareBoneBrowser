import os
import tkinter

from src.browser.layout import Layout

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100

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
        self.display_list = Layout(tokens).get_display_list()
        self.draw()

    def scrollDown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

    def scrollUp(self, e):
        self.scroll -= SCROLL_STEP
        self.draw()
