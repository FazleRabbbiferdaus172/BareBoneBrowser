import logging
import tkinter

from src.net.url import URL, ENTITY_MAPPING
from src.browser.ui import BrowserUI


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def show(body: str):
    """A very naive HTML renderer that strips out HTML tags and prints the text content."""
    in_tag: bool = False
    i = 0
    while i < len(body):
        if body[i] == "<":
            in_tag = True
        elif body[i] == ">":
            in_tag = False
        elif not in_tag:
            if body[i] == "&":
                try:
                    entitty_ening_index: int = body.index(";", i)
                    entity: str = body[i : entitty_ening_index + 1]
                    print(ENTITY_MAPPING[entity], end="")
                    i = entitty_ening_index + 1
                    continue
                except ValueError:
                    print(body[i], end="")
            else:
                print(body[i], end="")
        i += 1


def load(url: URL):
    """Load a URL and display its content."""
    if url.scheme == "file":
        body: str = url.load_file()
    elif url.scheme in ["http", "https", "view-source"]:
        body: str = url.request()
    elif url.scheme == "data":
        content_type, body = url.load_data()
        logger.debug(f"Data URL content type: {content_type}")
    show(body=body)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        load(URL())
    else:
        if sys.argv[1] == "--gui":
            browser_ui = BrowserUI()
            browser_ui.load()
            tkinter.mainloop()
        else:
            load(URL(sys.argv[1]))
