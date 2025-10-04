import io
import logging
import socket
import ssl
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
DEFAULT_FILE_URL = "file://" + os.path.abspath(os.path.join("tests", "test.html"))


class URL:
    def __init__(self, url: str | None = None):
        if url is None:
            url = DEFAULT_FILE_URL

        self.scheme: str
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https", "file"]
        if self.scheme in ["http", "https"]:
            self._process_http_url(url)
        elif self.scheme == "file":
            self._process_file_url(url)

    def _process_http_url(self, url):
        """Process an HTTP or HTTPS URL."""
        self.host: str
        self.path: str
        self.port: int
        if "/" not in url:
            url += "/"

        self.host, url = url.split("/", 1)
        self.path = "/" + url
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)
        else:
            if self.scheme == "http":
                self.port = 80
            elif self.scheme == "https":
                self.port = 443

        self.default_headers : dict[str, str] = {"Host": self.host, "User-Agent": "BareBoneBrowser/0.1", "Connection": "close"}

    def _process_file_url(self, url):
        """Process a file URL."""
        self.path = url

    def request(self, use_default_headres: bool = True, request_headers: dict[str, str] | None = None) -> str:
        """
        Make an HTTP request and return the response body as a string.
        param use_default_headres: Whether to use the default headers defined in the URL instance.
        param request_headers: Additional headers to include in the request.

        returns a sting of response body.
        """

        def generate_headers() -> str:
            """Generate the HTTP headers for the request."""
            headers: dict[str, str] = {}
            if use_default_headres:
                headers.update(self.default_headers)
            if request_headers is not None:
                headers.update(request_headers)
            headers_str: str = ""
            for header, value in headers.items():
                headers_str += f"{header}: {value}\r\n"
            headers_str += "\r\n"
            return headers_str

        s: socket.socket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP
        )
        s.connect((self.host, self.port))

        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, self.host)

        request: str
        request = "GET {} HTTP/1.0\r\n".format(self.path)
        request += generate_headers()
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
    
    def load_file(self) -> str:
        """Load a file and return its content as a string."""
        with open(self.path, "r", encoding="utf8") as f:
            return f.read()

def show(body: str):
    """A very naive HTML renderer that strips out HTML tags and prints the text content."""
    in_tag: bool = False

    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")


def load(url: URL):
    """Load a URL and display its content."""
    if url.scheme == "file":
        body: str = url.load_file()
    elif url.scheme in ["http", "https"]:
        body: str = url.request()
    show(body=body)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        load(URL())
    else:
        load(URL(sys.argv[1]))
