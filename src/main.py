import socket
import logging
import io


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class URL:
    def __init__(self, url: str):
        self.scheme: str
        self.host: str
        self.scheme, url = url.split("://", 1)
        assert self.scheme == "http"

        if "/" not in url:
            url += "/"

        self.host, url = url.split("/", 1)
        self.path = "/" + url

    def request(self) -> str:
        s: socket.socket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP
        )
        s.connect((self.host, 80))
        request: str
        request = "GET {} HTTP/1.0\r\n".format(self.path)
        request += "Host: {}\r\n".format(self.host)
        request += "\r\n"
        logger.debug(f"Request string: \n {request}")
        s.send(request.encode("utf8"))

        # makefile returns a file-like object containing every byte we receive from the server
        response: io.TextIOWrapper = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline: str = response.readline()
        version: str
        status: str
        explanation: str
        version, status, explanation = statusline.split(" ", 2)
        response_headers: dict = {}
        while True:
            line: str = response.readline()
            if line == "\r\n":
                break
            header: str
            value: str
            header, value = line.split(":", 1)
            response_headers[header] = value.strip()
        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers
        content: str = response.read()
        return content


def show(body: str):
    in_tag: bool = False

    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")


def load(url: URL):
    body: str = url.request()
    show(body=body)


if __name__ == "__main__":
    import sys

    load(URL(sys.argv[1]))
