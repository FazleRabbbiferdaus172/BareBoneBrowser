class Text:
    def __init__(self, text, parent=None):
        self.text = text
        self.children = []
        self.parent = parent

    def __str__(self):
        return self.text
    
    def __repr__(self):
        return self.text