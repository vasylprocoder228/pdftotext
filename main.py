import io
import requests
from pdfminer.converter import HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage

app = FastAPI()

@app.post('/extract_text')
async def extract_text(url: str, numOfPage: int = 1):
    # Download the PDF file
    response = requests.get(url)
    pdf_file = io.BytesIO(response.content)

    # Set up PDFMiner objects
    resource_manager = PDFResourceManager()
    output_string = io.BytesIO()
    laparams = LAParams()

    # Convert PDF to HTML
    converter = HTMLConverter(resource_manager, output_string, codec='utf-8', laparams=laparams)
    interpreter = PDFPageInterpreter(resource_manager, converter)

    for page in PDFPage.get_pages(pdf_file):
        interpreter.process_page(page)

    # Get HTML content
    html_content = output_string.getvalue().decode('utf-8')

    # Clean up resources
    converter.close()
    output_string.close()

    return {'html': html_content}
