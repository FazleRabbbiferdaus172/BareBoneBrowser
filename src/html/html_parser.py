from src.net.url import ENTITY_MAPPING
from src.html.tag import Element 
from src.html.text import Text

class HTMLParser:
    def __init__(self, body):
        self.body = body
        self.unfinished = []


    def parse(self, body: str) -> list[Element | Text]:
        """A very naive HTML renderer that parses html response and returns a list of tokens."""
        # logger.debug(body)
        in_tag: bool = False
        out: list[Element | Text] = []
        buffer: str = ""
        entity_buffer: str = ""
        in_entity: bool = False

        for c in body:
            if c == "<":
                in_tag = True
                if buffer:
                    # when some text like &ltrtre< as there is not ; then is was not entity
                    if entity_buffer and in_entity:
                        buffer += entity_buffer
                    out.append(Text(buffer))
                buffer = ""
                in_entity = False
                entity_buffer = ""
            elif c == ">":
                in_tag = False
                if buffer:
                    # when some text like &ltrtre> as there is not ; then is was not entity
                    if entity_buffer and in_entity:
                        buffer += entity_buffer
                    out.append(Element(buffer))
                buffer = ""
                in_entity = False
                entity_buffer = ""
            else:
                # might be enitity
                if c == "&":
                    in_entity = True
                    entity_buffer += c
                elif c == ";" and in_entity:
                    entity_buffer += c
                    buffer += ENTITY_MAPPING[entity_buffer]
                    in_entity = False
                    entity_buffer = ""
                elif not in_entity:
                    buffer += c
                else:
                    entity_buffer += c

        if not in_tag and buffer:
            out.append(Text(buffer))
        elif not in_tag and entity_buffer:
            out.append(Text(entity_buffer))
        # logger.debug(out)

        return out