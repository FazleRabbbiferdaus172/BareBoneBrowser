import tkinter

WIDTH, HEIGHT = 800, 600


class BrowserUI:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)
        self.canvas.pack()

    def load(self, content: str):
        self.canvas.create_text(100, 100, text=content)
