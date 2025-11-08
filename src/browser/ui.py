import tkinter

WIDTH, HEIGHT = 800, 600


def layout(text: str) -> list[int, int, str]:
    display_list = []
    HSTEP, VSTEP = 13, 18
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

    def draw(self):
        for x,y,c in self.display_list:
            self.canvas.create_text(x, y, text=c)

    def load(self, content: str):
        self.display_list = layout(content)
        self.draw()
