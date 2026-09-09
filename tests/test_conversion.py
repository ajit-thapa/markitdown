import unittest
import tempfile
import os
from markitdown import MarkItDown

class TestMarkItDownConversion(unittest.TestCase):
    def setUp(self):
        self.md = MarkItDown()

    def test_html_conversion(self):
        html_content = "<html><body><h1>Test Header</h1><p>Sample paragraph.</p></body></html>"
        with tempfile.NamedTemporaryFile("w+", suffix=".html", delete=False) as f:
            f.write(html_content)
            temp_path = f.name

        try:
            res = self.md.convert(temp_path)
            content = res.text_content if hasattr(res, "text_content") else str(res)
            self.assertIn("Test Header", content)
            self.assertIn("Sample paragraph", content)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == "__main__":
    unittest.main()
