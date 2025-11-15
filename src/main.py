import logging
import tkinter

from src.net.url import URL, ENTITY_MAPPING
from src.browser.ui import BrowserUI
from src.html.tag import Tag
from src.html.text import Text


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def lex(body: str) -> str:
    """A very naive HTML renderer that strips out HTML tags and prints the text content."""
    in_tag: bool = False
    out: list = []
    buffer: str = ""
    entity_buffer: str = ""
    result = ""
    in_entity: bool = False
    
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            if c == "&":
                in_entity = True
                entity_buffer += c
            elif c == ";":
                in_entity = False
                entity_buffer += c
                result += ENTITY_MAPPING[entity_buffer]
                entity_buffer = ""
            else:
                if in_entity:
                    entity_buffer += c
                else:
                    result += c
    return result


def show(body: str) -> None:
    """Display the body content in the UI."""
    text_content: str = lex(body)
    print(text_content, end="")

def fetch(url: URL) -> str:
    if url.scheme == "file":
        body: str = url.load_file()
    elif url.scheme in ["http", "https", "view-source"]:
        body: str = url.request()
    elif url.scheme == "data":
        content_type, body = url.load_data()
        logger.debug(f"Data URL content type: {content_type}")
    return body

def load(url: URL):
    """Load a URL and display its content."""
    body: str = fetch(url)
    show(body=body)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        load(URL())
    else:
        if sys.argv[1] == "--gui":
            browser_ui = BrowserUI()
            fetched_content = fetch(URL(sys.argv[2]) if len(sys.argv) > 2 else URL())
            lexed_content = lex(fetched_content)
            browser_ui.load(lexed_content)
            tkinter.mainloop()
        else:
            load(URL(sys.argv[1]))
