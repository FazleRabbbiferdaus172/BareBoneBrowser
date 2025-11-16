class Tag:
    def __init__(self, tag):
        self.tag = tag

    def __str__(self):
        return f"<{self.tag}>"

    def __repr__(self):
        return f"<{self.tag}>"
