import io
import logging
import os
import socket
import ssl
from collections import defaultdict

from src.cache.connection_cache import ConnectionCache

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
DEFAULT_FILE_URL: str = "file://" + os.path.abspath(os.path.join("tests", "test.html"))
ENTITY_MAPPING: defaultdict = defaultdict(lambda: "\u25A1", {"&lt;": "<", "&gt;": ">"})
Hierarchical_URL_SCHEMES: list[str] = ["http", "https", "file"]
OPAQUE_URL_SCHEMES: list[str] = ["data", "view-source"]


class URL:
    def __init__(self, url: str | None = None):
        if url is None:
            url = DEFAULT_FILE_URL

        self.scheme: str
        self.scheme, url = url.split(":", 1)
        assert self.scheme in Hierarchical_URL_SCHEMES + OPAQUE_URL_SCHEMES
        if self.scheme in Hierarchical_URL_SCHEMES:
            self._process_hierarchical_url(url)
        elif self.scheme in OPAQUE_URL_SCHEMES:
            self._process_opaque_url(url)

    def _process_hierarchical_url(self, url):
        """Process a hierarchical URL."""
        if self.scheme in ["http", "https"]:
            self._process_http_url(url[2:])
        elif self.scheme == "file":
            self._process_file_url(url[2:])
    
    def _process_opaque_url(self, url):
        """Process an opaque URL."""
        if self.scheme == "data":
            self._process_data_url(url)
        elif self.scheme == "view-source":
            self._process_view_source_url(url)
        
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

        self.default_headers: dict[str, str] = {
            "Host": self.host,
            "User-Agent": "BareBoneBrowser/0.1",
            # "Connection": "close",
            "Connection": "keep-alive",
        }

    def _process_file_url(self, url):
        """Process a file URL."""
        self.path = url

    def _process_data_url(self, url):
        """Process a data URL."""
        self._mime_type: str
        self._content: str
        self._mime_type, self._content = url.split(",", 1)

    def _process_view_source_url(self, url):
        """Process a view-source URL."""
        self.view_source_url = URL(url)

    def _request(
        self,
        use_default_headres: bool = True,
        request_headers: dict[str, str] | None = None,
    ) -> str:
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
        
        connection_cache: ConnectionCache  = ConnectionCache()
        s : socket.socket | None = connection_cache.get(self.host)
        if s is None:
            s = socket.socket(
                family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP
            )
            s.connect((self.host, self.port))

            if self.scheme == "https":
                ctx = ssl.create_default_context()
                s = ctx.wrap_socket(s, server_hostname=self.host)

            connection_cache.set(self.host, s)

        request: str
        request = "GET {} HTTP/1.0\r\n".format(self.path)
        request += generate_headers()
        request += "\r\n"
        logger.debug(f"Request string: \n {request}")
        s.send(request.encode("utf-8"))

        # makefile returns a file-like object containing every byte we receive from the server
        response: io.TextIOWrapper = s.makefile("rb", encoding="utf-8", newline="\r\n")
        statusline: str = response.readline()
        version: str
        status: str
        explanation: str
        version, status, explanation = statusline.decode('utf-8').split(" ", 2)
        response_headers: dict = {}
        while True:
            line: str = response.readline().decode('utf-8')
            if line == "\r\n":
                break
            header: str
            value: str
            header, value = line.split(":", 1)
            response_headers[header] = value.strip()
        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers
        content: str = ""
        if 'Content-Length' in response_headers:
            content = response.read(int(response_headers['Content-Length'])).decode('utf-8')
        else:
            content = response.read(int(response_headers['Content-Length'])).decode('utf-8')
        return content

    def request(self, use_default_headres: bool = True, request_headers: dict[str, str] | None = None,):
        content: str = ""
        if self.scheme == "view-source":
            content = self._replace_with_enities(self.view_source_url._request(use_default_headres, request_headers))
        else:
            content = self._request(use_default_headres, request_headers)
        return content
    
    def _replace_with_enities(self, content: str) -> str:
        """Replace special characters with their corresponding HTML entities."""
        for entity, char in ENTITY_MAPPING.items():
            content = content.replace(char, entity)
        return content

    def load_file(self) -> str:
        """Load a file and return its content as a string."""
        with open(self.path, "r", encoding="utf-8") as f:
            return f.read()

    def load_data(self) -> str:
        """Load a data URL and return its content as a string."""
        logger.debug(f"Data URL content type: {self._mime_type}")
        logger.debug(f"Data URL content: {self._content}")
        return self._mime_type, self._content


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
                    entitty_ening_index = body.index(";", i)
                    entity = body[i : entitty_ening_index + 1]
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
        load(URL(sys.argv[1]))
