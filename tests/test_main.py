import unittest
import sys
from io import StringIO
from unittest.mock import patch

from src.main import show, load, URL

class TestMain(unittest.TestCase):

    @patch('sys.stdout', new_callable=StringIO)
    def test_show_function_prints_chars_between_tags_only(self, mock_stdout):
        html_string = "<h1>Test</h1>"
        show(html_string)
        self.assertEqual(mock_stdout.getvalue(), "Test")

    @patch.object(URL, 'request')
    @patch('sys.stdout', new_callable=StringIO)
    def test_load_calls_url_request_and_show_to_print_content_in_output(self, mock_stdout, mock_request):
        mock_request.return_value = "<h1>Test</h1>"
        url = URL("http://test.com/test")
        load(url)
        self.assertEqual(mock_stdout.getvalue(), "Test")

    @patch('sys.stdout', new_callable=StringIO)
    def test_entities_support(self, mock_stdout):
        content = "&lt;&lt;&lt;&gt;&gt;&gt;"
        show(content)
        self.assertEqual(mock_stdout.getvalue(), "<<<>>>")

    @patch('sys.stdout', new_callable=StringIO)
    def test_similer_to_entity_text(self, mock_stdout):
        content = "&lt"
        show(content)
        self.assertEqual(mock_stdout.getvalue(), "&lt")
        content = "<h1>&lt</h1>"
        show(content)
        self.assertEqual(mock_stdout.getvalue(), "&lt")

if __name__ == "__main__":
    unittest.main(verbosity=2)

