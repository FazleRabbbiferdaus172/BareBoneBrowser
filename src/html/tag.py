class Element:
    def __init__(self, tag, parent=None):
        self.tag = tag
        self.children = []
        self.parent = parent

    def __str__(self):
        return f"<{self.tag}>"

    def __repr__(self):
        return f"<{self.tag}>"
