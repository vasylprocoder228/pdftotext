import requests
import pdfplumber
from fastapi import FastAPI
from fastapi import HTTPException
from PyPDF2 import PdfReader

app = FastAPI()

@app.post('/extract_text')
async def extract_text(url: str, numOfPage: int = 1):
    # Download the PDF file
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to download PDF")

    with open('temp.pdf', 'wb') as f:
        f.write(response.content)

    # Open the PDF file and extract text
    with pdfplumber.open('temp.pdf') as pdf:
        if 0 <= numOfPage <= len(pdf.pages) - 1:
            page = pdf.pages[numOfPage]
            extracted_text = page.extract_text()
            extracted_html = page.extract_text(xhtml=True)
        else:
            extracted_text = ''
            extracted_html = ''

    # Delete the temporary PDF file
    # Comment out the following line if you want to keep the downloaded file
    import os
    os.remove('temp.pdf')

    return {
        'text': extracted_text,
        'html': extracted_html,
        'numberOfPages': len(pdf.pages)
    }
