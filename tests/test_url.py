import unittest
import io
import ssl
from unittest.mock import patch, MagicMock

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

    def test_port_number_is_correctly_indentified(self):
        url_http_str: str = "http://test.com"
        url_https_str: str = "https://test.com"
        url_http_port_str: str = "http://test.com:8000"
        url_https_port_str: str = "https://test.com:8000"

        url: URL
        
        url = URL(url_http_str)
        self.assertEqual(url.port, 80)

        url = URL(url_http_port_str)
        self.assertEqual(url.port, 8000)

        url = URL(url_https_str)
        self.assertEqual(url.port, 443)

        url = URL(url_https_port_str)
        self.assertEqual(url.port, 8000)

    def test_correctly_append_ending_slash(self):
        url_str: str = "http://test.com"
        url: URL = URL(url_str)
        self.assertEqual(url.path, "/", "Fails to append endig /")

    @patch("socket.socket")
    def test_http_request(self, mock_socket):
        mock_socket_instance = mock_socket.return_value
        mock_socket_instance.send.return_value = 5
        return_mock_response = """HTTP/1.0 200 ok\r\nHost: test.com\r\nContent-Lenght: 5\r\n\r\nhello\r\n"""
        mock_socket_instance.makefile.return_value = io.StringIO(return_mock_response)
        url_str: str = "http://test.com"
        url: URL = URL(url_str)
        content: str = url.request()
        self.assertEqual(content.strip(), "hello")

    @patch("socket.socket")
    @patch("ssl.create_default_context")
    def test_https_request(self, mock_create_default_context, mock_socket):
        mock_socket_instance = mock_socket.return_value
        mock_socket_instance.send.return_value = 5
        return_mock_response = """HTTP/1.0 200 ok\r\nHost: test.com\r\nContent-Lenght: 5\r\n\r\nhello\r\n"""
        mock_socket_instance.makefile.return_value = io.StringIO(return_mock_response)

        mock_context_attrs = {"wrap_socket.return_value": mock_socket_instance}
        mock_context = MagicMock(**mock_context_attrs)
        mock_create_default_context.return_value = mock_context
        url_str: str = "https://test.com"
        url: URL = URL(url_str)
        content: str = url.request()
        mock_create_default_context.assert_called_once()
        mock_create_default_context.return_value.wrap_socket.assert_called_once()
        self.assertEqual(content.strip(), "hello")

    @patch("socket.socket")
    def test_http_request_has_content_and_user_agent_headers(self, mock_socket):
        mock_socket_instance = mock_socket.return_value
        mock_socket_instance.send.return_value = 5
        return_mock_response = """HTTP/1.0 200 ok\r\nHost: test.com\r\nContent-Lenght: 5\r\n\r\nhello\r\n"""
        mock_socket_instance.makefile.return_value = io.StringIO(return_mock_response)

        url_str: str = "http://test.com"
        url: URL = URL(url_str)
        url.request()
        send_method_args = mock_socket_instance.send.call_args.args[0]
        decodded_request_list: list[str] = send_method_args.decode("utf8").split("\r\n")
        self.assertIn("User-Agent: BareBoneBrowser/0.1", decodded_request_list)
        self.assertIn("Connection: close", decodded_request_list)

if __name__ == "__main__":
    unittest.main()
