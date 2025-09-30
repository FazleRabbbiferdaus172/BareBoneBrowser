import unittest
import io
from unittest.mock import patch

from src.main import URL


class TestUrl(unittest.TestCase):
    def test_scheme_host_path(self):
        url_1_str: str = "http://test.com/test"
        url_1: URL = URL(url_1_str)
        self.assertEqual(
            url_1.scheme, "http", f"Expected scheme should be http, got {url_1.scheme}"
        )
        self.assertEqual(
            url_1.host,
            "test.com",
            f"Expected host should be test.com, got {url_1.host}",
        )
        self.assertEqual(
            url_1.path, "/test", f"Expected path should be /test, got {url_1.path}"
        )

    def test_correctly_append_ending_slash(self):
        url_str: str = "http://test.com"
        url: URL = URL(url_str)
        self.assertEqual(url.path, "/", "Fails to append endig /")

    @patch("socket.socket")
    def test_request(self, mock_socket):
        mock_socket_instance = mock_socket.return_value
        mock_socket_instance.send.return_value = 5
        return_mock_response = """HTTP/1.0 200 ok\r\nHost: test.com\r\nContent-Lenght: 5\r\n\r\nhello\r\n"""
        mock_socket_instance.makefile.return_value = io.StringIO(return_mock_response)
        url_str: str = "http://test.com"
        url: URL = URL(url_str)
        content: str = url.request()
        self.assertEqual(content.strip(), "hello")


if __name__ == "__main__":
    unittest.main()
