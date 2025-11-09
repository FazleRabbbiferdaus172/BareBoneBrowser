import tkinter

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100


def layout(text: str) -> list[int, int, str]:
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP
        if cursor_x > WIDTH - HSTEP:
            cursor_x = HSTEP
            cursor_y += VSTEP
    return display_list

class BrowserUI:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)
        self.canvas.pack()
        self.scroll = 0
        self.window.bind("<Down>", self.scrollDown)
        self.window.bind("<Up>", self.scrollUp)

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
            self.canvas.create_text(x, y - self.scroll, text=c)

    def load(self, content: str):
        self.display_list = layout(content)
        self.draw()

    def scrollDown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

    def scrollUp(self, e):
        self.scroll -= SCROLL_STEP
        self.draw()
