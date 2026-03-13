from src.browser.layout import BlockLayout

class DocumentLayout:
    def __inti__(self, node):
        self.node = node
        self.parent = None
        self.children = []

    def layout(self):
        child = BlockLayout(self.node, self, None)
        self.children.append(child)
        child.layout()
        self.display_list = child.display_list
