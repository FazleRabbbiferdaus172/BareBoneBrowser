import io
import unittest
from unittest.mock import MagicMock, patch

from src.main import URL
from src.cache.connection_cache import ConnectionCache


class TestUrl(unittest.TestCase):
    def setUp(self) -> None:
        self.connetction_cache = ConnectionCache()

        self.socket_patcher = patch("socket.socket")
        self.ssl_create_default_context_patcher = patch("ssl.create_default_context")

        self.mock_socket = self.socket_patcher.start()
        self.mock_create_default_context = self.ssl_create_default_context_patcher.start()

        self.return_mock_response = """HTTP/1.0 200 ok\r\nHost: test.com\r\nContent-Length: 62\r\n\r\nhello\r\n""".encode("utf-8")
        self.mock_socket_instance = self.mock_socket.return_value
        self.mock_socket_instance.send.return_value = 5
        self.mock_socket_instance.makefile.return_value = io.BytesIO(self.return_mock_response)

        mock_context_attrs = {"wrap_socket.return_value": self.mock_socket_instance}
        self.mock_context = MagicMock(**mock_context_attrs)
        self.mock_create_default_context.return_value = self.mock_context

    def tearDown(self):
        self.connetction_cache.clear_cache()

        self.mock_socket = self.socket_patcher.stop()
        self.mock_create_default_context = self.ssl_create_default_context_patcher.stop()
    
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

    def test_http_request(self):
        url_str: str = "http://test.com"
        url: URL = URL(url_str)
        content: str = url.request()
        self.assertEqual(content.strip(), "hello")

    def test_https_request(self):
        url_str: str = "https://test.com"
        url: URL = URL(url_str)
        content: str = url.request()
        self.mock_create_default_context.assert_called_once()
        self.mock_create_default_context.return_value.wrap_socket.assert_called_once()
        self.assertEqual(content.strip(), "hello")

    @unittest.skip("Skipping for now as Connction close is not always expected")
    def test_http_request_has_content_and_user_agent_headers(self):
        url_str: str = "http://test.com"
        url: URL = URL(url_str)
        url.request()
        send_method_args = self.mock_socket_instance.send.call_args.args[0]
        decodded_request_list: list[str] = send_method_args.decode("utf-8").split("\r\n")
        self.assertIn("User-Agent: BareBoneBrowser/0.1", decodded_request_list)
        self.assertIn("Connection: close", decodded_request_list)

    def test_request_headres_replaces_deault_headers(self):
        url_str: str = "http://test.com"
        url: URL = URL(url_str)
        custom_headers: dict[str, str] = {
            "User-Agent": "TEST",
        }
        url.request(request_headers=custom_headers)
        send_method_args = self.mock_socket_instance.send.call_args.args[0]
        decodded_request_list: list[str] = send_method_args.decode("utf-8").split("\r\n")
        self.assertIn("User-Agent: TEST", decodded_request_list)
        self.assertIn("Host: test.com", decodded_request_list)

    @patch.object(URL, "_request", return_value="<html>test</html>")
    def test_view_source_url(self, mock_request):
        url_str: str = "view-source:http://test.com"
        url: URL = URL(url_str)
        self.assertEqual(
            url.scheme, "view-source", f"Expected scheme should be view-source, got {url.scheme}"
        )
        self.assertEqual(
            url.view_source_url.scheme,
            "http",
            f"Expected scheme should be http, got {url.view_source_url.scheme}",
        )
        self.assertEqual(
            url.view_source_url.host,
            "test.com",
            f"Expected host should be test.com, got {url.view_source_url.host}",
        )
        self.assertEqual(
            url.view_source_url.path,
            "/",
            f"Expected path should be /, got {url.view_source_url.path}",
        )
        content: str = url.request()
        self.assertEqual(
            content,
            "&lt;html&gt;test&lt;/html&gt;",
            f"Expected content should be &lt;html&gt;test&lt;/html&gt;, got {content}",
        )

    def test_sockets_are_reused_when_possible(self):
        url_str: str = "http://test.com"
        url: URL = URL(url_str)
        url.request()

        self.mock_socket_instance.makefile.return_value = io.BytesIO(self.return_mock_response)
        url_str: str = "http://test.com"
        url: URL = URL(url_str)
        url.request()
        
        self.assertEqual(self.mock_socket.call_count, 1)

    @unittest.skip("Not implemented yet")
    def test_redirects(self):
        """
            tests that redirect initiates new requests
        """
        pass


if __name__ == "__main__":
    unittest.main(verbosity=2)
