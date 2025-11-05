import io
import logging
import os
import socket
import ssl
from collections import defaultdict

from src.cache.connection_cache import ConnectionCache
from src.cache.cache_response import cache_response

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
DEFAULT_FILE_URL: str = "file://" + os.path.abspath(os.path.join("tests", "test.html"))
ENTITY_MAPPING: defaultdict = defaultdict(lambda: "\u25a1", {"&lt;": "<", "&gt;": ">"})
Hierarchical_URL_SCHEMES: list[str] = ["http", "https", "file"]
OPAQUE_URL_SCHEMES: list[str] = ["data", "view-source"]
MAX_REDIRECT_COUNT = 10


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

    # FIX: test is breaking because of this decorator
    @cache_response
    def _request(
        self,
        use_default_headres: bool = True,
        request_headers: dict[str, str] | None = None,
        redirect_count: int = 0,
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

        if redirect_count > MAX_REDIRECT_COUNT:
            logger.info("Max redirect reached.")
            return "Reached max redirect."
        connection_cache: ConnectionCache = ConnectionCache()
        s: socket.socket | None = connection_cache.get(self.host)
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
        content: str = ""
        response_headers: dict = {}
        try:
            version, status, explanation = statusline.decode("utf-8").split(" ", 2)

            while True:
                line: str = response.readline().decode("utf-8")
                if line == "\r\n":
                    break
                header: str
                value: str
                header, value = line.split(":", 1)
                response_headers[header] = value.strip()
            assert "transfer-encoding" not in response_headers
            assert "content-encoding" not in response_headers

            if "Content-Length" in response_headers:
                content = response.read(int(response_headers["Content-Length"])).decode(
                    "utf-8"
                )
            else:
                content = response.read(int(response_headers["Content-Length"])).decode(
                    "utf-8"
                )
            if int(status) >= 300 and int(status) < 400:
                redirect_url: URL = URL(response_headers["Location"])
                content = redirect_url._request(
                    use_default_headres=use_default_headres,
                    request_headers=request_headers,
                    redirect_count=redirect_count + 1,
                )
            return content
        except Exception as e:
            logger.error(f"Raised exception while parsing response : {e}")
            return "Check log something went worng"

    def request(
        self,
        use_default_headres: bool = True,
        request_headers: dict[str, str] | None = None,
    ):
        content: str = ""
        if self.scheme == "view-source":
            content = self._replace_with_enities(
                self.view_source_url._request(use_default_headres, request_headers)
            )
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
