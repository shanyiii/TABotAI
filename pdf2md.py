from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

from common import FILEPATH

def run_converter():
    converter = PdfConverter(
        artifact_dict=create_model_dict(),
    )
    rendered = converter(FILEPATH)
    markdown_output = rendered.markdown
    with open("marker_test_output.md", "w", encoding="utf-8") as f:
        f.write(markdown_output)

if __name__ == '__main__':
    run_converter()